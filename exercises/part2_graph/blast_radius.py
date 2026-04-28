"""
Exercise 2.2 — Blast radius (variable-length paths)
====================================================
The current implementation only finds DIRECT dependents. If `kafka-broker`
fails, we see `clickhouse-analytics` (which depends on Kafka) but NOT
`experiment-tracker` (which depends on ClickHouse).

We need to walk the DEPENDS_ON graph up to N hops backwards from the
failing service.

The reference implementation lives in src/memory/blast_radius.py.
"""

# TODO 2.2.a — replace this query with a variable-length path traversal.
#
#   - The current pattern  (aff)-[:DEPENDS_ON]->(root)  matches only direct
#     dependents (one hop).
#   - You want any service that has a path of length 1..N to the root.
#   - In Cypher, that's  -[:DEPENDS_ON*1..N]->.
#
# Why cap at N? Without a cap, Neo4j will follow cycles forever and explode.
# 4 is plenty for this topology (deepest real chain is 3).
#
# Also return the path so callers can show the cascade chain to the engineer.

BLAST_RADIUS_CYPHER = """
MATCH (aff:Service)-[:DEPENDS_ON]->(root:Service {name: $service})
RETURN aff.name AS name,
       aff.department AS dept,
       [aff.name, root.name] AS path_nodes
"""


# TODO 2.2.b — once your Cypher is right, this constant should respect
# the max_hops parameter. Use Python f-string formatting with `*1..{hops}`.
def blast_radius_cypher(max_hops: int = 4) -> str:
    """Return the Cypher with the configured max-hop ceiling."""
    return BLAST_RADIUS_CYPHER  # TODO: parameterize the {hops} placeholder.
