#!/usr/bin/env python3
"""Incident triage with live terminal UI showing vector, graph, and LLM activity."""

import sys
import threading

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.agents.graph import compile_triage_graph
from src.infrastructure.mock_apis import generate_incident, generate_random_incident
from src.tui.display import TriageTUI
from src.tui.events import Event, EventKind, clear_handler, emit, register_handler

console = Console()


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        service_name = sys.argv[1]
        template_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        incident = generate_incident(service_name, template_idx)
    else:
        incident = generate_random_incident()

    tui = TriageTUI(incident)
    register_handler(tui.handle_event)

    error: list[Exception] = []
    pipeline_done = threading.Event()

    def run_pipeline() -> None:
        try:
            graph = compile_triage_graph()
            initial_state = {
                "messages": [],
                "incident": incident,
                "service_name": "",
                "department": None,
                "department_knowledge": "",
                "blast_radius_report": None,
                "specialist_analysis": "",
                "final_report": "",
                "triage_classification": "",
                "routing_decision": "",
            }
            for _ in graph.stream(initial_state):
                pass
        except Exception as exc:
            error.append(exc)
        finally:
            pipeline_done.set()
            clear_handler()

    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()

    with Live(tui, refresh_per_second=10, console=console):
        pipeline_done.wait()

    thread.join(timeout=5)

    if error:
        console.print(f"\n[bold red]Pipeline error:[/] {error[0]}")
        raise error[0]

    # Final report outside Live
    analysis = tui.analysis
    if analysis:
        dept = ""
        if analysis.startswith("["):
            dept = analysis[1 : analysis.index("]")] if "]" in analysis else ""
            analysis = analysis[len(dept) + 2 :].strip()

        console.print()
        console.print(
            Panel(
                Text(analysis),
                title=f"[bold green]final report{f' · {dept}' if dept else ''}[/]",
                border_style="green",
                padding=(1, 2),
            )
        )


if __name__ == "__main__":
    main()
