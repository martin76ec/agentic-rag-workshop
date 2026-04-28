"""
Exercise 2.3 — Fusing vector and graph context
==============================================
Right now the prompt looks like this:

    ## Context
    {vector_chunks}

    Graph: {neighborhood_dict}
    Blast: {blast_report_dict}

    ## Question
    {query}

The dict dumps are nearly impossible for the LLM to ground on. Worse, the
graph context is appended last so it gets cut off when the prompt is long.

Fix: produce a STRUCTURED merge with priority order:
  1. Direct topology (depends_on / dependents) at the top — highest signal.
  2. Cascade paths (blast radius) next — concrete service chains.
  3. Vector chunks last — supporting facts.

Each section should be human-readable bullets, not dict reprs.
"""
from typing import Any


def fuse_context(
    *,
    query: str,
    vector_hits: list[dict[str, Any]],
    neighborhood: dict[str, Any],
    blast_paths: list[list[str]],
    affected_services: list[str],
) -> str:
    """Render a single, well-structured prompt body for the LLM.

    Args:
        query: free-text question.
        vector_hits: results from exercise 1.2.
        neighborhood: dict with keys 'depends_on', 'depended_by', 'tier', 'department'.
        blast_paths: list of cascade paths, e.g. [['kafka-broker', 'clickhouse', 'tracker']].
        affected_services: flat list of all services downstream of the failing one.

    Returns:
        A single prompt body string.
    """
    # TODO 2.3.a — build the topology section.
    # Format example:
    #   ### Topology (Neo4j)
    #   - Service tier: 1
    #   - Department: data
    #   - Depends on: k8s-controller
    #   - Depended on by: clickhouse-analytics, order-service, payment-service
    topology_section = ""

    # TODO 2.3.b — build the cascade section from blast_paths.
    # Render each path as an arrow chain:  kafka-broker → clickhouse → tracker
    # Limit to the first 5 paths to keep the prompt small.
    cascade_section = ""

    # TODO 2.3.c — build the supporting-context section from vector_hits.
    # Use the same renderer as exercise 1.3.
    supporting_section = ""

    # TODO 2.3.d — assemble in priority order: topology > cascade > supporting > question.
    return query
