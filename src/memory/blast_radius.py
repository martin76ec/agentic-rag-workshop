from mem0 import Memory

from src.infrastructure.models import BlastRadiusReport, Department, Severity
from src.infrastructure.topology import get_service_by_name
from src.tui.context import get_current_node
from src.tui.events import Event, EventKind, emit

_BLAST_CYPHER = """\
MATCH path = (aff:Service)-[:DEPENDS_ON*1..{hops}]->(root:Service {{name: $service}})
RETURN aff.name AS name, aff.department AS dept,
       [n IN nodes(path) | n.name] AS path_nodes"""


def _cypher_blast_radius(
    service_name: str,
    max_hops: int = 4,
) -> tuple[list[str], list[list[str]], list[Department]]:
    """Traverse the Neo4j graph to find all services that break when service_name fails."""
    from src.memory.config import get_neo4j_driver

    affected: list[str] = []
    seen: set[str] = set()
    paths: list[list[str]] = []
    seen_paths: set[tuple] = set()
    depts: set[Department] = set()

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            cypher = _BLAST_CYPHER.format(hops=max_hops)
            for rec in session.run(cypher, service=service_name):
                name = rec["name"]
                if name not in seen:
                    seen.add(name)
                    affected.append(name)
                try:
                    depts.add(Department(rec["dept"]))
                except ValueError:
                    pass
                # Reverse so path reads root → affected (causation direction)
                path_nodes = tuple(reversed(rec["path_nodes"]))
                if path_nodes not in seen_paths:
                    seen_paths.add(path_nodes)
                    paths.append(list(path_nodes))

            root_rec = session.run(
                "MATCH (s:Service {name: $service}) RETURN s.department AS dept",
                service=service_name,
            ).single()
            if root_rec:
                try:
                    depts.add(Department(root_rec["dept"]))
                except ValueError:
                    pass
    finally:
        driver.close()

    return affected, paths, list(depts)


def estimate_severity(affected_services: list[str], propagation_paths: list[list[str]]) -> Severity:
    service_objects = [get_service_by_name(name) for name in affected_services]
    service_objects = [s for s in service_objects if s is not None]

    if not service_objects:
        return Severity.INFO

    has_tier1 = any(s.tier == 1 for s in service_objects)
    has_tier2 = any(s.tier == 2 for s in service_objects)
    multi_department = len(set(s.department for s in service_objects)) > 1
    long_paths = any(len(p) > 2 for p in propagation_paths)

    if has_tier1 and multi_department and long_paths:
        return Severity.CRITICAL
    if has_tier1 and (multi_department or long_paths):
        return Severity.HIGH
    if has_tier1 or (has_tier2 and multi_department):
        return Severity.HIGH
    if has_tier2:
        return Severity.MEDIUM
    return Severity.LOW


def generate_blast_radius_report(
    incident_service: str,
    incident_id: str,
    memory: Memory | None = None,
    max_hops: int = 4,
) -> BlastRadiusReport:
    node = get_current_node()
    cypher = _BLAST_CYPHER.format(hops=max_hops)
    emit(Event(EventKind.GRAPH_BFS_START, node, {
        "service": incident_service,
        "label": f"blast radius from {incident_service}",
        "cypher": cypher,
    }))

    all_affected, all_paths, all_departments = _cypher_blast_radius(incident_service, max_hops)

    all_affected_severity = [incident_service] + all_affected
    estimated_impact = estimate_severity(all_affected_severity, all_paths)

    root_service = get_service_by_name(incident_service)
    recommended = []
    if root_service:
        if root_service.tier == 1:
            recommended.append(f"CRITICAL: {incident_service} is tier-1 — immediate response required")
        if len(all_departments) > 1:
            recommended.append(
                f"Cross-department impact ({len(all_departments)} departments) — coordinate across teams"
            )
        if len(all_affected) > 5:
            recommended.append("Wide blast radius — consider circuit breaker activation")
        for path in all_paths[:3]:
            if len(path) > 2:
                recommended.append(f"Cascading path detected: {' → '.join(path)}")

    report = BlastRadiusReport(
        incident_id=incident_id,
        root_service=incident_service,
        affected_services=all_affected,
        affected_departments=all_departments,
        propagation_paths=all_paths,
        estimated_impact=estimated_impact,
        recommended_actions=recommended,
    )
    emit(Event(EventKind.GRAPH_BFS_DONE, node, {
        "label": "blast_radius",
        "service": incident_service,
        "affected_services": all_affected,
        "departments": [d.value for d in all_departments],
        "impact": estimated_impact.value,
        "paths": [p for p in all_paths[:5] if len(p) >= 2],
    }))
    return report
