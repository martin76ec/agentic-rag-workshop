import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.agents.state import TriageState
from src.infrastructure.models import Department, Severity
from src.memory.blast_radius import generate_blast_radius_report
from src.memory.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, get_memory
from src.memory.graph import get_service_memory, query_service_graph_context, search_services
from src.tui.context import set_current_node
from src.tui.events import Event, EventKind, emit

TRIAGE_SYSTEM_PROMPT = """You are an infrastructure triage agent. Your job is to:
1. Identify which service is affected by the incident
2. Classify the incident severity
3. Determine which department owns the affected service
4. Retrieve context about the service from memory

Respond in JSON format:
{
    "service_name": "the affected service name",
    "severity_classification": "critical|high|medium|low",
    "department": "platform|data|product|ml|infra",
    "reasoning": "your reasoning",
    "context_found": "relevant context from memory about this service"
}"""


def triage_node(state: TriageState) -> dict:
    set_current_node("triage")
    emit(Event(EventKind.NODE_START, "triage"))

    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)
    memory = get_memory()

    incident = state.get("incident")
    if incident:
        incident_desc = (
            f"Incident: {incident.description} "
            f"(service: {incident.service_name}, "
            f"severity: {incident.severity.value})"
        )
    else:
        last_msg = state["messages"][-1].content if state["messages"] else ""
        incident_desc = last_msg

    prompt = f"""Analyze this infrastructure incident and classify it:

{incident_desc}

Available services: api-gateway, auth-service, config-service, service-mesh, postgres-primary,
redis-cache, kafka-broker, clickhouse-analytics, order-service, inventory-service,
payment-service, notification-service, feature-store, model-serving, training-pipeline,
experiment-tracker, k8s-controller, monitoring-agent, ci-runner, dns-resolver

Respond in JSON with: service_name, severity_classification, department, reasoning, context_found"""

    emit(Event(EventKind.LLM_START, "triage", {"label": "classifying incident"}))
    response = llm.invoke([SystemMessage(content=TRIAGE_SYSTEM_PROMPT), HumanMessage(content=prompt)])

    try:
        classification = json.loads(response.content)
    except json.JSONDecodeError:
        classification = {
            "service_name": incident.service_name if incident else "unknown",
            "severity_classification": "medium",
            "department": "platform",
            "reasoning": response.content,
            "context_found": "",
        }

    emit(Event(EventKind.LLM_DONE, "triage", {
        "preview": (
            f"service={classification.get('service_name')} "
            f"dept={classification.get('department')} "
            f"sev={classification.get('severity_classification')}"
        ),
    }))

    service_name = classification.get("service_name", "unknown")
    if incident:
        service_name = incident.service_name

    service_memory = get_service_memory(memory, service_name) if service_name != "unknown" else None
    context = ""
    if service_memory:
        context = service_memory.get("memory", "")
    else:
        search_results = search_services(memory, service_name, limit=3)
        context = "\n".join(r.get("memory", "") for r in search_results)

    # Enrich context with graph neighborhood from Neo4j
    graph_ctx: dict = {}
    if service_name != "unknown":
        graph_ctx = query_service_graph_context(service_name)
        if graph_ctx:
            parts = []
            if graph_ctx.get("depends_on"):
                parts.append(f"Depends on: {', '.join(graph_ctx['depends_on'])}")
            if graph_ctx.get("depended_by"):
                parts.append(f"Depended on by: {', '.join(graph_ctx['depended_by'][:6])}")
            if parts:
                context = (context + "\n" + "  ".join(parts)).strip()

    classification["context_found"] = context or classification.get("context_found", "")

    dept_str = classification.get("department", "platform")
    try:
        department = Department(dept_str)
    except ValueError:
        department = Department.PLATFORM

    sev_str = classification.get("severity_classification", "medium")
    try:
        severity = Severity(sev_str)
    except ValueError:
        severity = Severity.MEDIUM

    triage_classification = (
        f"Service: {service_name}\n"
        f"Severity: {severity.value}\n"
        f"Department: {department.value}\n"
        f"Reasoning: {classification.get('reasoning', 'N/A')}\n"
        f"Context: {context}"
    )

    blast_report = None
    if service_name != "unknown":
        incident_id = incident.incident_id if incident else "MANUAL"
        blast_report = generate_blast_radius_report(service_name, incident_id, memory)

    result = {
        "messages": [AIMessage(content=triage_classification)],
        "incident": incident,
        "service_name": service_name,
        "department": department,
        "triage_classification": triage_classification,
        "blast_radius_report": blast_report,
    }
    emit(Event(EventKind.NODE_DONE, "triage"))
    return result
