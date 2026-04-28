from mem0 import Memory
from neo4j import Driver

from src.infrastructure.models import Department, Service
from src.infrastructure.topology import SERVICES, get_dependents
from src.memory.config import get_memory, get_neo4j_driver
from src.tui.context import get_current_node
from src.tui.events import Event, EventKind, emit


def service_to_memory_content(service: Service) -> str:
    deps = ", ".join(service.depends_on) if service.depends_on else "none"
    tags = ", ".join(service.tags) if service.tags else "none"
    return (
        f"Service: {service.name}. "
        f"Department: {service.department.value}. "
        f"Description: {service.description}. "
        f"Tier: {service.tier} (1=critical, 2=important, 3=auxiliary). "
        f"Region: {service.region}. "
        f"Depends on: {deps}. "
        f"Tags: {tags}. "
        f"SLA target: {service.sla_minutes} minutes downtime per month."
    )


def service_to_metadata(service: Service) -> dict:
    dependents = [s.name for s in get_dependents(service.name)]
    return {
        "type": "service",
        "service_name": service.name,
        "department": service.department.value,
        "tier": str(service.tier),
        "region": service.region,
        "depends_on": ",".join(service.depends_on) if service.depends_on else "",
        "dependents": ",".join(dependents) if dependents else "",
        "tags": ",".join(service.tags) if service.tags else "",
    }


def seed_infrastructure(memory: Memory | None = None) -> dict[str, str]:
    if memory is None:
        memory = get_memory()

    results = {}
    for service in SERVICES:
        content = service_to_memory_content(service)
        metadata = service_to_metadata(service)
        result = memory.add(
            content,
            user_id="infrastructure",
            metadata=metadata,
            infer=True,
        )
        results[service.name] = result

    return results


def seed_department_knowledge(memory: Memory | None = None) -> dict[str, str]:
    if memory is None:
        memory = get_memory()

    department_knowledge = {
        Department.PLATFORM: (
            "Platform team owns API gateway, auth, config, and service mesh. "
            "All external traffic flows through api-gateway. auth-service handles OAuth2/OIDC. "
            "service-mesh provides mTLS and inter-service routing. "
            "Escalation: page platform-oncall for tier-1 incidents. "
            "Runbook: restart pods, check mesh proxy status, verify auth token validity."
        ),
        Department.DATA: (
            "Data team owns PostgreSQL, Redis, Kafka, and ClickHouse. "
            "postgres-primary is the source of truth for transactional data. "
            "redis-cache handles sessions and hot data. "
            "kafka-broker is the event backbone — all async communication flows through it. "
            "Escalation: page data-oncall for database outages. "
            "Runbook: check replication lag, failover replicas, clear Redis keys if corrupted."
        ),
        Department.PRODUCT: (
            "Product team owns orders, inventory, payments, and notifications. "
            "order-service and payment-service are tier-1 — any downtime is revenue loss. "
            "inventory-service requires Redis for real-time stock. "
            "notification-service is tier-2 but impacts customer experience. "
            "Escalation: page product-oncall for order/payment failures. "
            "Runbook: verify DB connections, check Kafka consumer lag, retry failed payments."
        ),
        Department.ML: (
            "ML team owns feature-store, model-serving, training-pipeline, and experiment-tracker. "
            "model-serving provides real-time inference — tier-2 but impacts recommendation revenue. "
            "training-pipeline is tier-3 — can tolerate delay. "
            "feature-store depends on Redis for online features and PostgreSQL for offline. "
            "Escalation: page ml-oncall for serving failures. "
            "Runbook: rollback model version, check feature freshness, restart training job."
        ),
        Department.INFRA: (
            "Infra team owns Kubernetes, monitoring, CI/CD, and DNS. "
            "k8s-controller is the control plane — if it's down, everything is at risk. "
            "monitoring-agent is critical for incident detection itself. "
            "dns-resolver affects service discovery across the entire platform. "
            "Escalation: page infra-oncall immediately for k8s or DNS issues. "
            "Runbook: kubectl get nodes, check CoreDNS logs, verify Prometheus targets."
        ),
    }

    results = {}
    for dept, knowledge in department_knowledge.items():
        result = memory.add(
            knowledge,
            user_id="infrastructure",
            metadata={
                "type": "department_knowledge",
                "department": dept.value,
            },
            infer=False,
        )
        results[dept.value] = result

    return results


def seed_neo4j_graph(driver: Driver | None = None) -> dict[str, int]:
    if driver is None:
        driver = get_neo4j_driver()

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        for service in SERVICES:
            session.run(
                """
                MERGE (s:Service {name: $name})
                SET s.department = $department,
                    s.tier = $tier,
                    s.region = $region,
                    s.description = $description,
                    s.sla_minutes = $sla_minutes,
                    s.tags = $tags
                MERGE (d:Department {name: $department})
                MERGE (s)-[:BELONGS_TO]->(d)
                """,
                name=service.name,
                department=service.department.value,
                tier=service.tier,
                region=service.region,
                description=service.description,
                sla_minutes=service.sla_minutes,
                tags=service.tags,
            )

        for service in SERVICES:
            for dep_name in service.depends_on:
                session.run(
                    """
                    MATCH (a:Service {name: $source}), (b:Service {name: $target})
                    MERGE (a)-[:DEPENDS_ON]->(b)
                    """,
                    source=service.name,
                    target=dep_name,
                )

        node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

    driver.close()
    return {"nodes": node_count, "relationships": rel_count}


_NEIGHBORHOOD_CYPHER = """\
MATCH (s:Service {name: $service})
OPTIONAL MATCH (s)-[:DEPENDS_ON]->(dep:Service)
OPTIONAL MATCH (aff:Service)-[:DEPENDS_ON]->(s)
RETURN s.tier AS tier, s.department AS dept,
       collect(DISTINCT dep.name) AS depends_on,
       collect(DISTINCT aff.name) AS depended_by"""


def query_service_graph_context(service_name: str) -> dict:
    """Query Neo4j for the service's immediate graph neighborhood."""
    node = get_current_node()
    emit(Event(EventKind.GRAPH_BFS_START, node, {
        "service": service_name,
        "label": f"neighborhood of {service_name}",
        "cypher": _NEIGHBORHOOD_CYPHER,
    }))

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            rec = session.run(_NEIGHBORHOOD_CYPHER, service=service_name).single()
    finally:
        driver.close()

    if not rec:
        emit(Event(EventKind.GRAPH_BFS_DONE, node, {
            "service": service_name,
            "affected_services": [],
            "departments": [],
            "impact": "unknown",
            "paths": [],
        }))
        return {}

    depends_on: list[str] = rec["depends_on"] or []
    depended_by: list[str] = rec["depended_by"] or []

    emit(Event(EventKind.GRAPH_BFS_DONE, node, {
        "label": "neighborhood",
        "service": service_name,
        "depends_on": depends_on,
        "depended_by": depended_by,
        "departments": [rec["dept"]] if rec["dept"] else [],
        "impact": f"tier {rec['tier']}",
    }))

    return {
        "tier": rec["tier"],
        "department": rec["dept"],
        "depends_on": depends_on,
        "depended_by": depended_by,
    }


def search_services(memory: Memory, query: str, limit: int = 5) -> list[dict]:
    node = get_current_node()
    emit(Event(EventKind.VECTOR_SEARCH_START, node, {"query": query}))
    results = memory.search(
        query,
        filters={"user_id": "infrastructure"},
        top_k=limit,
    )
    hits = [r for r in results.get("results", []) if r.get("metadata", {}).get("type") == "service"]
    emit(Event(EventKind.VECTOR_SEARCH_DONE, node, {"results": hits}))
    return hits


def get_service_memory(memory: Memory, service_name: str) -> dict | None:
    node = get_current_node()
    emit(Event(EventKind.VECTOR_SEARCH_START, node, {"query": service_name}))
    results = memory.search(
        f"Service: {service_name}",
        filters={"user_id": "infrastructure"},
        top_k=1,
    )
    hits = results.get("results", [])
    hit = next((h for h in hits if h.get("metadata", {}).get("service_name") == service_name), None)
    emit(Event(EventKind.VECTOR_SEARCH_DONE, node, {"results": [hit] if hit else []}))
    return hit
