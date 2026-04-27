#!/usr/bin/env python3
"""Run an incident through the triage pipeline end-to-end."""

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agents.graph import compile_triage_graph
from src.infrastructure.mock_apis import generate_incident, generate_random_incident
from src.infrastructure.models import Incident
from src.observability.decorators import init_agentops

console = Console()


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


def display_triage_result(state: dict) -> None:
    console.print(Panel(
        state.get("triage_classification", "No classification"),
        title="[bold yellow]Triage Classification[/]",
        border_style="yellow",
    ))

    routing = state.get("routing_decision", "Not routed")
    console.print(Panel(routing, title="[bold blue]Routing Decision[/]", border_style="blue"))

    blast = state.get("blast_radius_report")
    if blast:
        table = Table(title="Blast Radius Report")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        table.add_row("Root Service", blast.root_service)
        table.add_row("Estimated Impact", blast.estimated_impact.value)
        table.add_row("Affected Services", ", ".join(blast.affected_services) or "None")
        table.add_row("Affected Departments", ", ".join(d.value for d in blast.affected_departments))
        table.add_row("Propagation Paths", str(len(blast.propagation_paths)))
        table.add_row("Recommended Actions", "\n".join(blast.recommended_actions) or "None")
        console.print(table)

    analysis = state.get("specialist_analysis", "")
    if analysis:
        console.print(Panel(analysis, title="[bold green]Specialist Analysis[/]", border_style="green"))


def main() -> None:
    load_dotenv()
    init_agentops()

    if len(sys.argv) > 1:
        service_name = sys.argv[1]
        template_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
        incident = generate_incident(service_name, template_idx)
    else:
        incident = generate_random_incident()

    display_incident(incident)

    console.print("\n[bold]Running triage pipeline...[/]\n")

    graph = compile_triage_graph()

    result = graph.invoke({
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
    })

    display_triage_result(result)
    console.print("\n[bold green]Triage complete![/]")


if __name__ == "__main__":
    main()