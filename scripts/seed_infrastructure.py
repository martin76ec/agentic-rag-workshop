#!/usr/bin/env python3
"""Seed the infrastructure topology into Mem0."""

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.infrastructure.topology import SERVICES
from src.memory.config import get_memory
from src.memory.graph import seed_department_knowledge, seed_infrastructure, seed_neo4j_graph

console = Console()


def main() -> None:
    load_dotenv()
    console.print("[bold blue]Seeding infrastructure topology into Mem0...[/]")

    memory = get_memory()

    console.print(f"\n[bold]Loading {len(SERVICES)} services...[/]")
    service_results = seed_infrastructure(memory)
    table = Table(title="Services Seeded")
    table.add_column("Service", style="cyan")
    table.add_column("Department", style="green")
    table.add_column("Status", style="bold")
    for name, result in service_results.items():
        service = next(s for s in SERVICES if s.name == name)
        table.add_row(name, service.department.value, "[green]OK[/]")
    console.print(table)

    console.print("\n[bold]Loading department knowledge...[/]")
    dept_results = seed_department_knowledge(memory)
    for dept, result in dept_results.items():
        console.print(f"  [green]✓[/] {dept}")

    console.print("\n[bold]Seeding Neo4j knowledge graph...[/]")
    graph_stats = seed_neo4j_graph()
    console.print(
        f"  [green]✓[/] {graph_stats['nodes']} nodes  "
        f"[green]✓[/] {graph_stats['relationships']} relationships"
    )

    console.print("\n[bold green]Infrastructure seeding complete![/]")


if __name__ == "__main__":
    main()