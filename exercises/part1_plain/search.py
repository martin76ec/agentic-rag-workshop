"""
Exercise 1.2 — Top-k and metadata filtering
===========================================
The on-call engineer types "kafka-broker is down" and the system returns
a SINGLE result that's sometimes for `kafka-broker` and sometimes for
`clickhouse-analytics` because both mention Kafka in their description.

Two problems:
  1. k=1 — one bad hit means a useless answer.
  2. No metadata filter — we mix infrastructure docs with department knowledge,
     and we have no way to scope by department or tier.

Fix: bump k to a sensible default and accept optional metadata filters.
"""
from typing import Any

from mem0 import Memory


def search(memory: Memory, query: str, *, department: str | None = None) -> list[dict[str, Any]]:
    """Search infrastructure memory and return service hits.

    Args:
        memory: a Mem0 instance backed by Qdrant.
        query: free-text query from the on-call engineer.
        department: optional filter — when set, only return services owned by
            that department.

    Returns:
        A list of hit dicts with keys 'memory' and 'metadata'.
    """
    # TODO 1.2.a — fix top-k. One result is not enough for triage.
    # Pick a number large enough to surface neighbors but small enough that
    # the LLM prompt doesn't blow up. The reference uses 5.
    top_k = 1

    # TODO 1.2.b — pass a `filters` dict to memory.search() that scopes
    # results to user_id="infrastructure". Without this, we'd also retrieve
    # any unrelated memories stored in Mem0.
    #
    # Hint: filters = {"user_id": "infrastructure"}
    results = memory.search(query, top_k=top_k)

    # TODO 1.2.c — keep only entries where metadata.type == "service".
    # Department-knowledge entries (`type == "department_knowledge"`) leak
    # into the results otherwise.
    hits = results.get("results", [])

    # TODO 1.2.d — when `department` is provided, drop hits whose metadata
    # department does not match. Use the metadata field exactly as written
    # by service_to_metadata() in src/memory/graph.py.
    if department:
        pass

    return hits
