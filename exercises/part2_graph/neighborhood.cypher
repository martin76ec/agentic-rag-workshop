// Exercise 2.1 — Neighborhood query
// ===================================
// This query should return, for a given service:
//   - tier and department
//   - direct dependencies (services it depends_on)
//   - direct dependents (services that depend on it)
//
// Right now we only return the service's own properties. The graph traversal
// is missing. Your job: add the OPTIONAL MATCH clauses that walk the
// DEPENDS_ON edges in both directions.
//
// The reference implementation lives in src/memory/graph.py
// (constant `_NEIGHBORHOOD_CYPHER`). Try it yourself first.

MATCH (s:Service {name: $service})

// TODO 2.1.a — add an OPTIONAL MATCH that walks outbound DEPENDS_ON edges:
//   (s)-[:DEPENDS_ON]->(dep:Service)
// and collect the dep names.

// TODO 2.1.b — add an OPTIONAL MATCH that walks inbound DEPENDS_ON edges:
//   (aff:Service)-[:DEPENDS_ON]->(s)
// and collect the aff names. These are the services that BREAK if `s` fails.

RETURN s.tier   AS tier,
       s.department AS dept,
       []           AS depends_on,    // TODO 2.1.c — replace [] with collect(DISTINCT dep.name)
       []           AS depended_by    // TODO 2.1.d — replace [] with collect(DISTINCT aff.name)
