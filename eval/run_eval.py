"""
Run retrieval evaluation against the current src/ implementation.

Usage:
    uv run python -m eval.run_eval                 # default: vector-only retrieval, k=5
    uv run python -m eval.run_eval --mode graph    # vector + neighborhood + blast radius
    uv run python -m eval.run_eval --k 10          # top-k=10

Output is a small markdown table showing recall@k, precision@k, MRR per query
plus the macro mean. Run before and after each Track-A part to see your
fixes lift the metrics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.metrics import (
    aggregate,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

GOLD_PATH = Path(__file__).parent / "gold_set.json"


def load_gold() -> list[dict]:
    return json.loads(GOLD_PATH.read_text())["items"]


def retrieve_vector(query: str, k: int) -> list[str]:
    """Vector-only retrieval using the project's reference implementation."""
    from src.memory.config import get_memory
    from src.memory.graph import search_services

    memory = get_memory()
    hits = search_services(memory, query, limit=k)
    return [h.get("metadata", {}).get("service_name") for h in hits if h.get("metadata", {}).get("service_name")]


def retrieve_graph(query: str, k: int) -> list[str]:
    """Vector + Neo4j neighborhood for the top-1 hit."""
    from src.memory.blast_radius import _cypher_blast_radius
    from src.memory.config import get_memory
    from src.memory.graph import query_service_graph_context, search_services

    memory = get_memory()
    hits = search_services(memory, query, limit=k)
    services = [h["metadata"]["service_name"] for h in hits if h.get("metadata", {}).get("service_name")]
    if not services:
        return []
    root = services[0]
    neigh = query_service_graph_context(root)
    affected, _, _ = _cypher_blast_radius(root, max_hops=4)
    extras = list(neigh.get("depended_by") or []) + list(affected)
    seen: set[str] = set()
    out: list[str] = []
    for svc in [root, *services[1:], *extras]:
        if svc and svc not in seen:
            seen.add(svc)
            out.append(svc)
    return out[:k]


RETRIEVERS = {
    "vector": retrieve_vector,
    "graph": retrieve_graph,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval quality on the gold set.")
    parser.add_argument("--mode", choices=list(RETRIEVERS), default="vector")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    retriever = RETRIEVERS[args.mode]
    gold = load_gold()

    rows: list[tuple[str, float, float, float]] = []
    recalls: list[float] = []
    precisions: list[float] = []
    rrs: list[float] = []

    for item in gold:
        query = item["query"]
        expected = item["expected_services"]
        retrieved = retriever(query, args.k)
        r = recall_at_k(retrieved, expected, args.k)
        p = precision_at_k(retrieved, expected, args.k)
        rr = reciprocal_rank(retrieved, expected)
        rows.append((query, r, p, rr))
        recalls.append(r)
        precisions.append(p)
        rrs.append(rr)

    print(f"\nRetrieval evaluation — mode={args.mode}, k={args.k}, n={len(gold)}\n")
    print(f"{'query':<60} {'R@k':>6} {'P@k':>6} {'RR':>6}")
    print("-" * 80)
    for q, r, p, rr in rows:
        snippet = (q[:57] + "...") if len(q) > 60 else q
        print(f"{snippet:<60} {r:>6.2f} {p:>6.2f} {rr:>6.2f}")
    print("-" * 80)
    print(
        f"{'mean':<60} "
        f"{aggregate(recalls):>6.2f} "
        f"{aggregate(precisions):>6.2f} "
        f"{aggregate(rrs):>6.2f}"
    )


if __name__ == "__main__":
    main()
