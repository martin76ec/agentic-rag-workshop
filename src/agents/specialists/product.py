from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.agents.state import TriageState
from src.memory.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, get_memory
from src.memory.graph import search_services
from src.tui.events import Event, EventKind, emit

PRODUCT_SYSTEM_PROMPT = (
    "You are a Product department specialist agent. You own: "
    "order-service, inventory-service, payment-service, "
    "notification-service.\n\n"
    "Your expertise:\n"
    "- Order lifecycle and transaction integrity\n"
    "- Inventory real-time stock management and Redis caching\n"
    "- Payment processing, Stripe integration, and idempotency\n"
    "- Notification delivery across email, SMS, and push channels\n\n"
    "Given an incident and context, provide:\n"
    "1. Root cause hypothesis\n"
    "2. Immediate mitigation steps\n"
    "3. Long-term remediation\n"
    "4. Impact assessment on product services and revenue"
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

    search_results = search_services(memory, f"product {service_name} order inventory payment notification", limit=5)
    memory_context = "\n".join(r.get("memory", "") for r in search_results)

    prompt = f"""Analyze this product service incident:

Service: {service_name}
Triage: {triage}
Blast radius: {blast_summary}
Memory context: {memory_context}

Provide root cause, mitigation, remediation, and revenue impact assessment."""

    emit(Event(EventKind.LLM_START, "specialist", {"label": "product analysis"}))
    response = llm.invoke([SystemMessage(content=PRODUCT_SYSTEM_PROMPT), HumanMessage(content=prompt)])
    emit(Event(EventKind.LLM_DONE, "specialist", {"preview": response.content[:150]}))

    return {
        "department_knowledge": memory_context,
        "specialist_analysis": f"[PRODUCT] {response.content}",
    }
