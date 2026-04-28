# Agentic RAG Workshop

> Build intuition for *why* agentic RAG exists by running the same incident
> through three progressively more powerful modes and comparing what each one
> knows — and doesn't know.

**Duration:** ~90 minutes  
**Prerequisites:** Setup complete (`make setup && make seed`)

---

## The Scenario

You are on-call. A message arrives:

> **kafka-broker** is returning 5xx errors. Consumer lag is growing.
> Services are failing to connect.

Your job: figure out what broke, what else is at risk, and what to do about it.

You'll run this same incident through three modes. Each time, the system gets
more context and makes better decisions. By the end you'll see exactly where
"retrieval" ends and "agentic" begins.

---

## The Three Modes

```
Mode 1: Plain RAG          Mode 2: Graph RAG          Mode 3: Agentic RAG
─────────────────          ─────────────────          ───────────────────
Incident                   Incident                   Incident
   │                          │                          │
   ▼                          ▼                          ▼
[Vector Search]           [Vector Search]          ┌─ Triage Agent ─┐
   │                          │                    │  vector search │
   ▼                       [Neo4j: neighborhood]   │  graph queries │
[LLM]                         │                    └────────────────┘
   │                       [Neo4j: blast radius]          │
   ▼                          │                    ┌─ Router Agent ─┐
 Response                     ▼                    │ pick specialist│
                           [LLM]                   └────────────────┘
                              │                          │
                              ▼                   ┌─ Specialist ───┐
                           Response               │  vector search │
                                                  │  LLM (expert) │
                                                  └────────────────┘
                                                         │
                                                         ▼
                                                    Final Report
```

**The key question to carry through all three modes:**
*What does the system know that it didn't know in the previous mode, and
how does that change the response?*

---

## Part 0 — Setup (5 min)

If you haven't already:

```bash
make setup    # start Qdrant + Neo4j, create .env
make seed     # load 20 services into Qdrant and Neo4j
```

Verify both stores have data:

```bash
make inspect-mem    # shows Qdrant contents (should list 20 services)
make browse-graph   # opens Neo4j browser at http://localhost:7474
                    # run: MATCH (n) RETURN n   to see the topology
```

**While you wait for Neo4j to open**, look at `src/infrastructure/topology.py`.
This is the ground truth — 20 services, 5 departments, dependency edges.
Both Qdrant (vector) and Neo4j (graph) are seeded from this same file.

---

## Part 1 — Plain RAG (20 min)

**What it does:** one Qdrant search → one LLM call. Nothing else.

```bash
make rag kafka-broker
```

Watch the TUI. You'll see exactly one `vector` tool call followed by one `llm` call.

### What to observe

- What did the vector search return? (top results by score)
- Did the LLM know which services depend on kafka-broker?
- Did it mention `order-service`, `payment-service`, `notification-service`,
  `clickhouse-analytics`, `training-pipeline`?
- How specific were the mitigation steps?

### Discussion questions

1. The LLM was told kafka-broker is a Kafka cluster. Where did that come from?
   (Check the vector result — it came from Qdrant, not the LLM's weights.)

2. The LLM probably mentioned "downstream services might be affected" in vague
   terms. Why? What information is missing?

3. If you were on-call and received this response at 3am, what would you
   still not know?

### The gap

Plain RAG retrieves *facts about the service* from the vector store.
It does not know *how the service connects to everything else*.
The topology is in Neo4j — but we never queried it.

---

## Part 2 — Graph RAG (20 min)

**What it adds:** two Cypher queries against Neo4j before calling the LLM.

```bash
make graph-rag kafka-broker
```

Watch the TUI. Now you'll see:
- `vector` — same Qdrant search as before
- `graph · neighborhood of kafka-broker` — direct deps/dependents from Neo4j
- `graph · blast radius from kafka-broker` — variable-length path traversal

### What to observe

Compare the graph tool call results to Part 1:

| What Plain RAG knew | What Graph RAG adds |
|---------------------|---------------------|
| Kafka is a tier-1 data service | Exactly 5 services depend on it |
| Kafka handles async messaging | The cascade path: kafka → clickhouse → experiment-tracker |
| Kafka team owns it | 3 departments (data, product, ml) are in the blast radius |

- Did the LLM response change? In what ways?
- Is the blast radius in the response *exact* or still estimated?
- What Cypher query did the graph tool run?

### Understanding the Cypher

The blast radius query is:
```cypher
MATCH path = (aff:Service)-[:DEPENDS_ON*1..4]->(root:Service {name: $service})
RETURN aff.name, aff.department, [n IN nodes(path) | n.name] AS path_nodes
```

This finds every service `aff` that has a directed `DEPENDS_ON` path
(up to 4 hops) leading to kafka-broker. If kafka-broker fails, all of
those services fail with it.

Try modifying it in Neo4j browser:
```cypher
MATCH path = (aff:Service)-[:DEPENDS_ON*1..4]->(root:Service {name: 'kafka-broker'})
RETURN path
```

You should see the cascade visualised as a graph.

### The gap

Graph RAG knows the blast radius *precisely*. But it still gives every incident
the same generic treatment. A kafka outage and a postgres outage get the same
system prompt, the same retrieval query, the same LLM. There's no specialisation.

What if we could route to an expert who knows Kafka-specific runbooks?

---

## Part 3 — Agentic RAG (25 min)

**What it adds:** the system decides how to retrieve, what expertise to apply,
and which specialist to route to — driven by the incident content.

```bash
make tui kafka-broker
```

Now watch the full pipeline unfold in real time.

### What to observe

**Triage Agent:**
- Two graph queries (neighborhood + blast radius) plus a vector search
- The LLM classifies: service name, severity, department — this *decision*
  determines everything that follows

**Router Agent:**
- Reads the blast radius departments from state
- Decides: `data` specialist (kafka is data), flags CROSS-DEPARTMENT

**Specialist Agent [data]:**
- A *second* vector search — this one targeted at data-specific knowledge
- A *second* LLM call — with a system prompt that says "you are a data
  infrastructure expert who owns Kafka, Postgres, Redis, ClickHouse"
- The response should reference Kafka-specific runbooks and escalation paths

### Compare the three responses side by side

Run each mode for the same service in separate terminal tabs:
```bash
make rag kafka-broker        # tab 1
make graph-rag kafka-broker  # tab 2
make tui kafka-broker        # tab 3
```

| Question | Plain RAG | Graph RAG | Agentic RAG |
|----------|-----------|-----------|-------------|
| Which services are at risk? | Vague | Exact (5 named) | Exact + departments |
| Who should be paged? | Generic | Generic | data-oncall specifically |
| What Kafka command to run? | Unlikely | Unlikely | Likely (specialist knows) |
| How many LLM calls? | 1 | 1 | 2 (triage + specialist) |
| How many retrieval steps? | 1 | 3 | 4-5 |

### The "agentic" moment

Notice that the router's decision is *not hardcoded*. It reads
`blast_radius_report.affected_departments` from state — information
that was retrieved from Neo4j by the triage agent. The retrieval
*informs* the routing, which *determines* what gets retrieved next.

This is the core of agentic RAG:
> **Retrieval is not a fixed step. It's a decision made by the agent
> based on what it has already learned.**

---

## Part 4 — Exploration (15 min)

### Try different failure points

```bash
make tui api-gateway       # tier-1 platform — cascades to almost everything
make tui k8s-controller    # infra — cascades to all departments
make tui experiment-tracker # tier-3 ml — small blast radius
make tui postgres-primary   # data — big blast radius through product
```

For each run, predict before it completes:
- Which specialist will be called?
- How many services are in the blast radius?
- Which departments are affected?

Then verify your prediction in the TUI.

### Read the code path for one incident

Pick `kafka-broker` and trace what happens:

```
src/infrastructure/mock_apis.py    → generates the Incident object
src/agents/triage.py               → calls search_services() + query_service_graph_context()
src/memory/graph.py                → emits VECTOR_SEARCH events, runs Qdrant query
src/memory/blast_radius.py         → emits GRAPH_BFS events, runs Cypher query
src/agents/router.py               → reads blast_radius_report from state, picks department
src/agents/specialists/data.py     → calls search_services() again (dept-specific query)
src/tui/display.py                 → renders everything you see in the terminal
```

Every event shown in the TUI corresponds to exactly one of these calls.

### Modify something

**Easy — add an incident template:**

Open `src/infrastructure/mock_apis.py` and add to `INCIDENT_TEMPLATES`:

```python
{
    "description": "Consumer group lag exceeding 100k messages on {service}",
    "severity": Severity.HIGH,
    "symptoms": ["consumer_lag", "message_backlog", "processing_delay"],
},
```

Then run `make tui kafka-broker 8` (index 8 = your new template).

**Medium — add a service:**

1. Add to `src/infrastructure/topology.py`:

```python
Service(
    name="audit-log",
    department=Department.PLATFORM,
    description="Immutable audit log service for compliance",
    tier=2,
    region="us-east-1",
    depends_on=["kafka-broker", "postgres-primary"],
    sla_minutes=26.28,
    tags=["audit", "compliance"],
    metadata={"port": 8095, "protocol": "http", "owners": ["platform-team"]},
),
```

2. Re-seed: `make seed`

3. Run: `make tui audit-log`

Observe: the blast radius of kafka-broker now includes audit-log. The
graph query discovers it automatically — you didn't change any agent code.

---

## Summary

| Concept | Where it lives |
|---------|---------------|
| Vector store (Qdrant) | `src/memory/graph.py` → `search_services()` |
| Knowledge graph (Neo4j) | `src/memory/graph.py` → `query_service_graph_context()` |
| Graph traversal (Cypher) | `src/memory/blast_radius.py` → `_cypher_blast_radius()` |
| Agent state | `src/agents/state.py` → `TriageState` |
| Routing decision | `src/agents/router.py` → reads blast radius from state |
| Specialist dispatch | `src/agents/specialist_coordinator.py` |
| Live TUI events | `src/tui/events.py` → `emit()` called at every retrieval/LLM step |

### The one-line answer

**Plain RAG** retrieves facts.
**Graph RAG** retrieves facts *and* relationships.
**Agentic RAG** decides *what* to retrieve, *from where*, and *who should act on it* —
dynamically, based on what was already learned.

---

## Further Challenges

**If you finish early:**

1. **Reflect and re-retrieve:** After the specialist generates its analysis,
   add a reflection step that checks confidence and re-runs the vector search
   with a more specific query if the analysis seems shallow.

2. **Cross-department incident:** Trigger a k8s-controller failure. The router
   flags it as CROSS-DEPARTMENT. What if you wanted to call *all* affected
   department specialists in parallel? (Hint: `langgraph.graph.Send`)

3. **Memory across incidents:** After each triage, write the specialist analysis
   back into Qdrant tagged with the service name. On the next incident for the
   same service, the triage retrieves it as prior context. Does the response improve?

4. **Replace Cypher with LLM reasoning:** In `blast_radius.py`, comment out
   `_cypher_blast_radius()` and replace it with an LLM that reasons about
   cascading failures from the vector context alone. Compare accuracy against
   the Cypher ground truth.
