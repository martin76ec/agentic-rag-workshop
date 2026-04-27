#!/usr/bin/env python3
"""Run an incident through the triage pipeline end-to-end."""

import sys
import time

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agents.graph import compile_triage_graph
from src.infrastructure.mock_apis import generate_incident, generate_random_incident
from src.infrastructure.models import BlastRadiusReport, Incident
from src.observability.decorators import (
    begin_session,
    end_session,
    init_agentops,
    record_node_event,
)

console = Console()

NODE_STYLES = {
    "triage": ("yellow", "Triage Agent"),
    "router": ("blue", "Router Agent"),
    "specialist": ("green", "Specialist Agent"),
}
NODE_ORDER = ["triage", "router", "specialist"]
_SKIP = {"messages", "incident"}


def display_incident(incident: Incident) -> None:
    console.print(Panel(
        f"[bold]Incident ID:[/] {incident.incident_id}\n"
        f"[bold]Service:[/] {incident.service_name}\n"
        f"[bold]Severity:[/] {incident.severity.value}\n"
        f"[bold]Description:[/] {incident.description}\n"
        f"[bold]Symptoms:[/] {', '.join(incident.symptoms)}",
        title="[bold red]Incoming Incident[/]",
        border_style="red",
    ))


def _fmt(val) -> str:
    if val is None:
        return "[dim]—[/]"
    if hasattr(val, "value"):
        return str(val.value)
    s = str(val)
    return s[:400] + "[dim]…[/]" if len(s) > 400 else s


def display_node_output(node_name: str, state_delta: dict, elapsed: float) -> None:
    color, label = NODE_STYLES.get(node_name, ("white", node_name.title()))

    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column("Field", style=f"bold {color}", min_width=26, no_wrap=True)
    table.add_column("Value", overflow="fold")

    for key, val in state_delta.items():
        if key in _SKIP:
            continue
        if key == "blast_radius_report" and isinstance(val, BlastRadiusReport):
            table.add_row(
                key,
                f"root=[bold]{val.root_service}[/]  "
                f"impact=[bold]{val.estimated_impact.value}[/]  "
                f"affected={len(val.affected_services)} services  "
                f"depts={', '.join(str(d) for d in val.affected_departments)}",
            )
        else:
            table.add_row(key, _fmt(val))

    console.print(Panel(
        table,
        title=f"[bold {color}]{label}[/]  [dim]{elapsed:.1f}s[/]",
        border_style=color,
    ))


def _print_node_rule(node_idx: int) -> None:
    if node_idx < len(NODE_ORDER):
        color, label = NODE_STYLES[NODE_ORDER[node_idx]]
        console.rule(f"[{color}]Running {label}…[/]")


def main() -> None:
    load_dotenv()
    init_agentops()
    session = begin_session()

    if len(sys.argv) > 1:
        service_name = sys.argv[1]
        template_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        incident = generate_incident(service_name, template_idx)
    else:
        incident = generate_random_incident()

    display_incident(incident)
    console.print()

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

    node_idx = 0
    t_prev = time.time()
    _print_node_rule(node_idx)

    try:
        for chunk in graph.stream(initial_state):
            t_now = time.time()
            node_name, state_delta = next(iter(chunk.items()))
            elapsed = t_now - t_prev
            display_node_output(node_name, state_delta, elapsed)
            record_node_event(node_name, state_delta, elapsed)
            t_prev = t_now
            node_idx += 1
            console.print()
            _print_node_rule(node_idx)
        end_session(session, success=True)
    except Exception as exc:
        console.print(f"\n[bold red]Pipeline error:[/] {exc}")
        end_session(session, success=False)
        raise

    console.print("[bold green]Triage complete.[/]")


if __name__ == "__main__":
    main()
