from langgraph.graph import END, START, StateGraph

from src.agents.router import router_node
from src.agents.specialist_coordinator import specialist_node
from src.agents.state import TriageState
from src.agents.triage import triage_node


def should_route_to_specialist(state: TriageState) -> str:
    department = state.get("department")
    if department is None:
        return "router"
    return "specialist"


def build_triage_graph() -> StateGraph:
    graph = StateGraph(TriageState)

    graph.add_node("triage", triage_node)
    graph.add_node("router", router_node)
    graph.add_node("specialist", specialist_node)

    graph.add_edge(START, "triage")
    graph.add_edge("triage", "router")
    graph.add_edge("router", "specialist")
    graph.add_edge("specialist", END)

    return graph


def compile_triage_graph():
    graph = build_triage_graph()
    return graph.compile()
