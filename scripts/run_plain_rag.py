#!/usr/bin/env python3
"""
Mode 1 — Plain RAG: one vector search + one LLM call.
No agents, no graph, no routing. Baseline to compare against.
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
from src.memory.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, get_memory
from src.memory.graph import search_services
from src.tui.context import set_current_node
from src.tui.display import TriageTUI
from src.tui.events import Event, EventKind, clear_handler, emit, register_handler

console = Console()

_SYSTEM = """You are an on-call infrastructure engineer.
Given an incident and any retrieved context, respond with:
1. Root cause hypothesis
2. Immediate mitigation steps
3. Which other services might be affected

Be concise. You only have the context below — do not assume topology you were not given."""


def run(incident) -> str:
    set_current_node("rag")
    emit(Event(EventKind.NODE_START, "rag"))

    memory = get_memory()
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)

    results = search_services(memory, incident.service_name, limit=5)
    context = "\n".join(r.get("memory", "") for r in results) or "No context found."

    prompt = f"""Incident: {incident.description}
Service:  {incident.service_name}
Severity: {incident.severity.value}
Symptoms: {', '.join(incident.symptoms)}

Retrieved context:
{context}

Provide root cause hypothesis, immediate mitigation, and affected services."""

    emit(Event(EventKind.LLM_START, "rag", {"label": "generating response"}))
    response = llm.invoke([SystemMessage(content=_SYSTEM), HumanMessage(content=prompt)])
    emit(Event(EventKind.LLM_DONE, "rag", {"preview": response.content[:150]}))
    emit(Event(EventKind.NODE_DONE, "rag", {"analysis": response.content}))

    return response.content


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        service_name = sys.argv[1]
        template_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        incident = generate_incident(service_name, template_idx)
    else:
        incident = generate_random_incident()

    tui = TriageTUI(incident, stages=[("rag", "Plain RAG")])
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
        console.print(Panel(Text(tui.analysis), title="[bold cyan]plain RAG response[/]", border_style="cyan", padding=(1, 2)))


if __name__ == "__main__":
    main()
