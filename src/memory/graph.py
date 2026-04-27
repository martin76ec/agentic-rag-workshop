from mem0 import Memory

from src.infrastructure.models import Department, Service
from src.infrastructure.topology import SERVICES, get_dependents
from src.memory.config import get_memory


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
            infer=False,
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


def search_services(memory: Memory, query: str, limit: int = 5) -> list[dict]:
    results = memory.search(
        query,
        filters={"user_id": "infrastructure"},
        top_k=limit,
    )
    return [r for r in results.get("results", []) if r.get("metadata", {}).get("type") == "service"]


def get_service_memory(memory: Memory, service_name: str) -> dict | None:
    results = memory.search(
        f"Service: {service_name}",
        filters={"user_id": "infrastructure"},
        top_k=1,
    )
    hits = results.get("results", [])
    for hit in hits:
        if hit.get("metadata", {}).get("service_name") == service_name:
            return hit
    return None
