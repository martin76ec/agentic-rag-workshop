from src.agents.state import TriageState
from src.infrastructure.models import Department

ROUTING_PROMPT_TEMPLATE = """Route this incident to the appropriate department specialist.

Service: {service_name}
Department: {department}
Severity: {severity}
Blast radius: {blast_summary}

Available departments: platform, data, product, ml, infra

Respond with just the department name."""


def router_node(state: TriageState) -> dict:
    department = state.get("department")
    if department:
        routing_decision = f"Routing to {department.value} specialist"
    else:
        service_name = state.get("service_name", "")
        department = Department.INFRA
        if any(k in service_name for k in ["api-gateway", "auth", "config", "mesh"]):
            department = Department.PLATFORM
        elif any(k in service_name for k in ["postgres", "redis", "kafka", "clickhouse"]):
            department = Department.DATA
        elif any(k in service_name for k in ["order", "inventory", "payment", "notification"]):
            department = Department.PRODUCT
        elif any(k in service_name for k in ["feature", "model", "training", "experiment"]):
            department = Department.ML
        routing_decision = f"Auto-routing to {department.value} specialist based on service name"

    blast_report = state.get("blast_radius_report")
    departments_involved = []
    if blast_report:
        departments_involved = [d.value for d in blast_report.affected_departments]

    cross_dept = len(departments_involved) > 1
    if cross_dept:
        routing_decision += f" — CROSS-DEPARTMENT: {', '.join(departments_involved)}"

    return {
        "department": department,
        "routing_decision": routing_decision,
    }
