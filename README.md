<div align="center">

<br/>

<img src="assets/demo.svg" width="780" alt="Live TUI — kafka-broker incident running through the agentic pipeline"/>

<br/>

# Agentic RAG Workshop

**Build intuition for retrieval-augmented generation by running the same<br/>
infrastructure incident through three progressively more powerful modes.**

<br/>

[![Python](https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-stateful_agents-FF6B35?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-vector_store-DC244C?style=for-the-badge)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-graph_db-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)

<br/>

</div>

---

## The Core Idea

Three modes. One incident — `kafka-broker` failure. Watch how the system's
understanding of *what* to retrieve, and *who* to route to, evolves with each step.

<br/>

<div align="center">

|  | Plain RAG | Graph RAG | Agentic RAG |
|:--|:--:|:--:|:--:|
| **Retrieval strategy** | Fixed vector search | Vector + 2 Cypher queries | Agent decides what to retrieve |
| **Blast radius** | Vague estimates | Exact named services | Named services + departments + escalation |
| **Who gets paged** | Generic advice | Generic advice | `data-oncall` specifically |
| **Specialist knowledge** | — | — | Kafka-specific runbooks |
| **LLM calls** | `1` | `1` | `2` (triage + specialist) |
| **Retrieval steps** | `1` | `3` | `4 – 5` |

</div>

<br/>

> [!NOTE]
> **Retrieval is not a fixed step. It is a decision made by the agent based on what it has already learned.**

---

## Workshop

The full guided workshop is in [`WORKSHOP.md`](WORKSHOP.md) — ~90 min, 4 parts.

Run all three modes in separate terminals and compare outputs side by side:

```bash
make rag kafka-broker        # Part 1 — plain RAG: one search, one LLM call
make graph-rag kafka-broker  # Part 2 — add Neo4j topology queries
make tui kafka-broker        # Part 3 — full agentic pipeline with live TUI
```

---

## Quick Start

> **Prerequisites:** [uv](https://docs.astral.sh/uv/) · [Docker](https://www.docker.com/) · [Ollama](https://ollama.com)

```bash
# 1. Pull models (one-time, ~20 GB)
ollama pull gemma4:31b-cloud
ollama pull nomic-embed-text-v2-moe

# 2. Start Qdrant + Neo4j, create .env, install deps
make setup

# 3. Seed 20 services into Qdrant (vector) + Neo4j (graph)
make seed

# 4. Run the full agentic pipeline
make tui kafka-broker
```

Verify both stores have data before running:

```bash
make inspect-mem    # lists all documents in Qdrant
make browse-graph   # opens Neo4j browser → run: MATCH (n) RETURN n
```

---

## Architecture

```
                         ┌──────────────────────────────────────┐
   Incident input        │           PLAIN RAG                  │
   kafka-broker  ──────▶ │  Vector Search → LLM → Response      │
                         └──────────────────────────────────────┘

                         ┌──────────────────────────────────────┐
                         │           GRAPH RAG                  │
                ──────▶  │  Vector Search                        │
                         │  + Neo4j: service neighborhood        │
                         │  + Neo4j: blast radius traversal      │
                         │  → LLM → Response                     │
                         └──────────────────────────────────────┘

                         ┌──────────────────────────────────────────────────────────┐
                         │                   AGENTIC RAG                            │
                         │                                                          │
                         │   ┌──────────────────────────────────────────────────┐   │
                ──────▶  │   │  Triage Agent                                    │   │
                         │   │  · vector search (Mem0 / Qdrant)                 │   │
                         │   │  · Neo4j: service neighborhood                   │   │
                         │   │  · Neo4j: blast radius (DEPENDS_ON*1..4)         │   │
                         │   │  · LLM: classify service, severity, department   │   │
                         │   └────────────────────────┬─────────────────────────┘   │
                         │                            │                             │
                         │              state: service_name, severity,              │
                         │              department, blast_radius_report             │
                         │                            │                             │
                         │                            ▼                             │
                         │   ┌──────────────────────────────────────────────────┐   │
                         │   │  Router Agent                                    │   │
                         │   │  · reads blast_radius_report.affected_departments│   │
                         │   │  · selects specialist node                       │   │
                         │   └────────────────────────┬─────────────────────────┘   │
                         │                            │                             │
                         │                            ▼                             │
                         │   ┌──────────────────────────────────────────────────┐   │
                         │   │  Specialist Agent  [data]                        │   │
                         │   │  · targeted vector search                        │   │
                         │   │  · Kafka-expert system prompt                    │   │
                         │   │  · root cause analysis + runbooks                │   │
                         │   └──────────────────────────────────────────────────┘   │
                         └──────────────────────────────────────────────────────────┘
```

**The "agentic" moment:** the router reads `blast_radius_report.affected_departments`
from shared state — data that the triage agent retrieved from Neo4j.
Retrieval *informs* routing, which *determines* what gets retrieved next.

---

## Infrastructure Topology

20 services across 5 departments, seeded into both Qdrant and Neo4j
from a single source of truth at `src/infrastructure/topology.py`:

```
  platform ──── api-gateway ──▶ auth-service
                             ──▶ config-service
                             ──▶ service-mesh
                                      │
  data ─────────────────────────────  ▼
                             ──▶ postgres-primary
                             ──▶ redis-cache
                             ──▶ kafka-broker
                                      │
  product ──────────────────────────  ▼
                             ──▶ order-service
                             ──▶ payment-service
                             ──▶ notification-service

  ml ─────── postgres-primary ──▶ feature-store ──▶ model-serving
                                                ──▶ experiment-tracker

  infra ───── k8s-controller ──▶ monitoring-agent
                              ──▶ ci-runner
                              ──▶ dns-resolver
```

Adding a service to `topology.py` and re-running `make seed` automatically
updates both stores — no agent code changes required.

---

## Code Map

```
src/
├── infrastructure/
│   ├── topology.py          ← 20 services, 5 departments — single source of truth
│   ├── models.py            ← Service, Incident, BlastRadiusReport, Severity
│   └── mock_apis.py         ← incident templates for testing
│
├── memory/
│   ├── config.py            ← Mem0 + Neo4j driver setup
│   ├── graph.py             ← seed/search Qdrant; neighborhood Cypher queries
│   └── blast_radius.py      ← DEPENDS_ON*1..4 traversal, severity estimation
│
├── agents/
│   ├── state.py             ← TriageState — shared across all LangGraph nodes
│   ├── triage.py            ← vector search + graph queries + LLM classification
│   ├── router.py            ← reads blast_radius_report, picks specialist
│   ├── graph.py             ← LangGraph: triage → router → specialist → END
│   └── specialists/         ← platform · data · product · ml · infra
│       ├── platform.py
│       ├── data.py
│       ├── product.py
│       ├── ml.py
│       └── infra.py
│
└── tui/
    ├── events.py            ← emit() / register_handler() event bus
    ├── context.py           ← thread-local current_node tracking
    └── display.py           ← TriageTUI Rich live display

scripts/
├── run_plain_rag.py         ← make rag
├── run_graph_rag.py         ← make graph-rag
└── run_triage_tui.py        ← make tui
```

Every event shown in the TUI maps to exactly one `emit()` call in the
memory or agent layer — traceable line by line.

---

## Configuration

`.env` is created by `make setup` from `.env.example`. Override any value:

| Variable | Default | Description |
|:--|:--|:--|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_LLM_MODEL` | `gemma4:31b-cloud` | Reasoning model |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `NEO4J_URL` | `bolt://localhost:7687` | Neo4j bolt endpoint |
| `NEO4J_USERNAME` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |

---

## Development

```bash
make test      # run pytest
make lint      # run ruff
make check     # lint + test
make stop      # stop Docker services
make clean     # remove venv + volumes
```

---

<div align="center">

See [`WORKSHOP.md`](WORKSHOP.md) for guided exercises and extension challenges.

</div>
