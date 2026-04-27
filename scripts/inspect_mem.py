#!/usr/bin/env python3
"""Inspect all documents stored in Mem0/Qdrant and the Neo4j knowledge graph."""

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.memory.config import (
    COLLECTION_NAME,
    NEO4J_PASSWORD,
    NEO4J_URL,
    NEO4J_USERNAME,
    OLLAMA_BASE_URL,
    OLLAMA_EMBEDDING_MODEL,
    get_memory,
)

console = Console()

TIER_LABELS = {"1": "critical", "2": "important", "3": "auxiliary"}


def main() -> None:
    load_dotenv()

    console.print(
        f"[bold]Connecting to Mem0/Qdrant[/]  "
        f"[dim]collection={COLLECTION_NAME}  embedder={OLLAMA_EMBEDDING_MODEL}  ollama={OLLAMA_BASE_URL}[/]"
    )

    memory = get_memory()

    raw = memory.get_all(user_id="infrastructure")
    entries = raw.get("results", []) if isinstance(raw, dict) else list(raw)

    if not entries:
        console.print("\n[yellow]No memories found. Run [bold]make seed[/bold] first.[/]")
        sys.exit(0)

    services = [e for e in entries if e.get("metadata", {}).get("type") == "service"]
    dept_docs = [e for e in entries if e.get("metadata", {}).get("type") == "department_knowledge"]
    other = [e for e in entries if e not in services and e not in dept_docs]

    console.print(
        f"\n[bold]Total:[/] {len(entries)}  "
        f"[green]{len(services)} services[/]  "
        f"[blue]{len(dept_docs)} dept knowledge[/]  "
        f"[dim]{len(other)} other[/]\n"
    )

    # ── Services ──────────────────────────────────────────────────────────────
    if services:
        table = Table(title=f"[bold green]Services ({len(services)})[/]", border_style="green")
        table.add_column("Service", style="bold")
        table.add_column("Dept")
        table.add_column("Tier", justify="center")
        table.add_column("Depends On")
        table.add_column("Dependents")
        table.add_column("Tags")

        for entry in sorted(
            services,
            key=lambda e: (e.get("metadata", {}).get("tier", "9"), e.get("metadata", {}).get("service_name", "")),
        ):
            meta = entry.get("metadata", {})
            tier_raw = meta.get("tier", "?")
            tier_label = TIER_LABELS.get(tier_raw, tier_raw)
            table.add_row(
                meta.get("service_name", "?"),
                meta.get("department", "?"),
                f"{tier_raw} ({tier_label})",
                meta.get("depends_on", "") or "—",
                meta.get("dependents", "") or "—",
                meta.get("tags", "") or "—",
            )

        console.print(table)
        console.print()

    # ── Department knowledge ──────────────────────────────────────────────────
    if dept_docs:
        console.rule("[bold blue]Department Knowledge[/]")
        for entry in sorted(dept_docs, key=lambda e: e.get("metadata", {}).get("department", "")):
            dept = entry.get("metadata", {}).get("department", "unknown")
            content = entry.get("memory", "")
            console.print(Panel(content, title=f"[bold blue]{dept}[/]", border_style="blue"))
        console.print()

    # ── Unclassified ──────────────────────────────────────────────────────────
    if other:
        console.rule("[dim]Unclassified[/]")
        for entry in other:
            mem_id = entry.get("id", "?")
            preview = str(entry.get("memory", ""))[:120]
            console.print(f"  [dim]{mem_id}:[/] {preview}")

    # ── Neo4j knowledge graph ─────────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]Neo4j Knowledge Graph[/]")
    try:
        from neo4j import GraphDatabase  # noqa: PLC0415

        driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

            console.print(f"\n[bold]{node_count} nodes[/]  [dim]·[/]  [bold]{rel_count} relationships[/]\n")

            if node_count == 0:
                console.print("[yellow]Graph is empty. Run [bold]make seed[/bold] to populate.[/]")
            else:
                # Relationships table
                rels = session.run(
                    "MATCH (a)-[r]->(b) RETURN a.name AS src, type(r) AS rel, b.name AS dst "
                    "ORDER BY src, rel LIMIT 100"
                ).data()

                if rels:
                    table = Table(title="[bold magenta]Relationships[/]", border_style="magenta")
                    table.add_column("Source", style="bold")
                    table.add_column("Relationship")
                    table.add_column("Target")
                    for row in rels:
                        table.add_row(
                            str(row.get("src", "?")),
                            str(row.get("rel", "?")),
                            str(row.get("dst", "?")),
                        )
                    console.print(table)

        driver.close()
    except Exception as exc:
        console.print(f"[yellow]Could not connect to Neo4j ({NEO4J_URL}): {exc}[/]")
        console.print("[dim]Start it with: docker compose up -d neo4j[/]")


if __name__ == "__main__":
    main()
