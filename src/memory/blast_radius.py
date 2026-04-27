from collections import deque

from mem0 import Memory

from src.infrastructure.models import BlastRadiusReport, Department, Severity
from src.infrastructure.topology import get_service_by_name


def compute_blast_radius(
    service_name: str,
    max_hops: int = 4,
) -> tuple[list[str], list[list[str]], list[Department]]:
    all_affected = set()
    propagation_paths: list[list[str]] = []
    affected_departments: set[Department] = set()

    service = get_service_by_name(service_name)
    if not service:
        return [], [], []

    affected_departments.add(service.department)

    queue: deque[tuple[str, int, list[str]]] = deque()
    queue.append((service_name, 0, [service_name]))

    while queue:
        current, hops, path = queue.popleft()
        if hops >= max_hops:
            continue

        current_service = get_service_by_name(current)
        if not current_service:
            continue

        for dependent_name in current_service.depends_on:
            if dependent_name in all_affected:
                new_path = path + [dependent_name]
                propagation_paths.append(new_path)
                continue

            all_affected.add(dependent_name)
            dependent_service = get_service_by_name(dependent_name)
            if dependent_service:
                affected_departments.add(dependent_service.department)

            new_path = path + [dependent_name]
            propagation_paths.append(new_path)
            queue.append((dependent_name, hops + 1, new_path))

    return list(all_affected), propagation_paths, list(affected_departments)


def compute_upstream_blast_radius(
    service_name: str,
    max_hops: int = 4,
) -> tuple[list[str], list[list[str]], list[Department]]:
    all_affected = set()
    propagation_paths: list[list[str]] = []
    affected_departments: set[Department] = set()

    service = get_service_by_name(service_name)
    if not service:
        return [], [], []

    affected_departments.add(service.department)

    queue: deque[tuple[str, int, list[str]]] = deque()
    queue.append((service_name, 0, [service_name]))

    while queue:
        current, hops, path = queue.popleft()
        if hops >= max_hops:
            continue

        from src.infrastructure.topology import get_dependents

        dependents = get_dependents(current)
        for dep in dependents:
            if dep.name in all_affected:
                new_path = path + [dep.name]
                propagation_paths.append(new_path)
                continue

            all_affected.add(dep.name)
            affected_departments.add(dep.department)

            new_path = path + [dep.name]
            propagation_paths.append(new_path)
            queue.append((dep.name, hops + 1, new_path))

    return list(all_affected), propagation_paths, list(affected_departments)


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
    downstream_affected, downstream_paths, downstream_depts = compute_blast_radius(
        incident_service, max_hops
    )
    upstream_affected, upstream_paths, upstream_depts = compute_upstream_blast_radius(
        incident_service, max_hops
    )

    all_affected = list(set(downstream_affected + upstream_affected))
    all_paths = downstream_paths + upstream_paths
    all_departments = list(set(downstream_depts + upstream_depts))

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

    return BlastRadiusReport(
        incident_id=incident_id,
        root_service=incident_service,
        affected_services=all_affected,
        affected_departments=all_departments,
        propagation_paths=all_paths,
        estimated_impact=estimated_impact,
        recommended_actions=recommended,
    )
