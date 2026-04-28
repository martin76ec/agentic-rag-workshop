from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.agents.state import TriageState
from src.memory.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, get_memory
from src.memory.graph import search_services
from src.tui.events import Event, EventKind, emit

INFRA_SYSTEM_PROMPT = (
    "You are an Infra department specialist agent. You own: "
    "k8s-controller, monitoring-agent, ci-runner, dns-resolver.\n\n"
    "Your expertise:\n"
    "- Kubernetes control plane, node health, and pod scheduling\n"
    "- Prometheus/Grafana monitoring stack and alerting rules\n"
    "- CI/CD pipelines (GitHub Actions, ArgoCD) and deployment health\n"
    "- DNS resolution (CoreDNS) and service discovery\n\n"
    "Given an incident and context, provide:\n"
    "1. Root cause hypothesis\n"
    "2. Immediate mitigation steps\n"
    "3. Long-term remediation\n"
    "4. Impact assessment — note that infra failures "
    "often cascade to ALL departments"
)


def analyze(state: TriageState) -> dict:
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)
    memory = get_memory()

    service_name = state.get("service_name", "unknown")
    triage = state.get("triage_classification", "")
    blast = state.get("blast_radius_report")
    blast_summary = ""
    if blast:
        blast_summary = f"Affected: {', '.join(blast.affected_services[:5])}. Impact: {blast.estimated_impact.value}"

    search_results = search_services(memory, f"infra {service_name} k8s monitoring dns ci", limit=5)
    memory_context = "\n".join(r.get("memory", "") for r in search_results)

    prompt = f"""Analyze this infrastructure incident:

Service: {service_name}
Triage: {triage}
Blast radius: {blast_summary}
Memory context: {memory_context}

Provide root cause, mitigation, remediation, and impact assessment. Remember infra failures can cascade widely."""

    emit(Event(EventKind.LLM_START, "specialist", {"label": "infra analysis"}))
    response = llm.invoke([SystemMessage(content=INFRA_SYSTEM_PROMPT), HumanMessage(content=prompt)])
    emit(Event(EventKind.LLM_DONE, "specialist", {"preview": response.content[:150]}))

    return {
        "department_knowledge": memory_context,
        "specialist_analysis": f"[INFRA] {response.content}",
    }
