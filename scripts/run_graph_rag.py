#!/usr/bin/env python3
"""
Mode 2 — Graph RAG: vector search + Neo4j graph queries + one LLM call.
No agents, no routing. Shows what the graph adds over plain vectors.
"""

import sys
import threading

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.infrastructure.mock_apis import generate_incident, generate_random_incident
from src.memory.blast_radius import generate_blast_radius_report
from src.memory.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, get_memory
from src.memory.graph import query_service_graph_context, search_services
from src.tui.context import set_current_node
from src.tui.display import TriageTUI
from src.tui.events import Event, EventKind, clear_handler, emit, register_handler

console = Console()

_SYSTEM = """You are an on-call infrastructure engineer with access to a live topology graph.
Given an incident, retrieved vector context, and graph-derived topology data, respond with:
1. Root cause hypothesis
2. Immediate mitigation steps
3. Blast radius — exact services and departments at risk
4. Propagation paths — how the failure cascades

Use the graph data to be specific about downstream impact."""


def run(incident) -> str:
    set_current_node("graph_rag")
    emit(Event(EventKind.NODE_START, "graph_rag"))

    memory = get_memory()
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)

    # ── Vector retrieval ────────────────────────────────────────────────
    results = search_services(memory, incident.service_name, limit=5)
    vector_context = "\n".join(r.get("memory", "") for r in results) or "No context found."

    # ── Graph queries ───────────────────────────────────────────────────
    graph_ctx = query_service_graph_context(incident.service_name)
    blast = generate_blast_radius_report(incident.service_name, incident.incident_id)

    graph_block = ""
    if graph_ctx:
        graph_block = (
            f"Tier: {graph_ctx.get('tier')}  Department: {graph_ctx.get('department')}\n"
            f"Depends on:   {', '.join(graph_ctx.get('depends_on', [])) or '—'}\n"
            f"Depended on by: {', '.join(graph_ctx.get('depended_by', [])) or '—'}\n"
        )

    blast_block = ""
    if blast and blast.affected_services:
        paths_text = "\n".join(
            f"  {' → '.join(p)}" for p in blast.propagation_paths[:4] if len(p) >= 2
        )
        blast_block = (
            f"Affected ({len(blast.affected_services)}): "
            f"{', '.join(blast.affected_services)}\n"
            f"Departments: {', '.join(d.value for d in blast.affected_departments)}\n"
            f"Impact: {blast.estimated_impact.value}\n"
            f"Propagation paths:\n{paths_text}"
        )

    prompt = f"""Incident: {incident.description}
Service:  {incident.service_name}
Severity: {incident.severity.value}
Symptoms: {', '.join(incident.symptoms)}

=== Vector Knowledge Base ===
{vector_context}

=== Graph: Service Topology ===
{graph_block or 'Service not found in graph.'}

=== Graph: Blast Radius (Cypher traversal) ===
{blast_block or 'No downstream impact found.'}

Provide root cause, mitigation, blast radius analysis, and cascade risks."""

    emit(Event(EventKind.LLM_START, "graph_rag", {"label": "generating response (vector + graph context)"}))
    response = llm.invoke([SystemMessage(content=_SYSTEM), HumanMessage(content=prompt)])
    emit(Event(EventKind.LLM_DONE, "graph_rag", {"preview": response.content[:150]}))
    emit(Event(EventKind.NODE_DONE, "graph_rag", {"analysis": response.content}))

    return response.content


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        service_name = sys.argv[1]
        template_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        incident = generate_incident(service_name, template_idx)
    else:
        incident = generate_random_incident()

    tui = TriageTUI(incident, stages=[("graph_rag", "Graph RAG")])
    register_handler(tui.handle_event)

    error: list[Exception] = []
    done = threading.Event()

    def _run() -> None:
        try:
            run(incident)
        except Exception as exc:
            error.append(exc)
        finally:
            done.set()
            clear_handler()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    with Live(tui, refresh_per_second=10, console=console):
        done.wait()

    thread.join(timeout=5)

    if error:
        console.print(f"\n[bold red]Error:[/] {error[0]}")
        raise error[0]

    if tui.analysis:
        console.print()
        console.print(Panel(Text(tui.analysis), title="[bold magenta]graph RAG response[/]", border_style="magenta", padding=(1, 2)))


if __name__ == "__main__":
    main()
