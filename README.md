<div align="center">

# Agentic RAG Workshop

**Build intuition for retrieval-augmented generation by running the same
infrastructure incident through three progressively more powerful modes.**

[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-stateful_agents-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-local_LLM-000000?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-vector_store-DC244C?style=flat-square)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-graph_db-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)

<br/>

<img src="assets/demo.svg" width="720" alt="Live TUI demo — kafka-broker incident running through the agentic pipeline"/>

</div>

---

## The Idea

Three modes. Same incident (`kafka-broker` failure). Watch how the system's
understanding of *what* to retrieve — and *who* should handle it — evolves.

| | Plain RAG | Graph RAG | Agentic RAG |
|:--|:--:|:--:|:--:|
| **How retrieval works** | Fixed vector search | Fixed vector + 2 Cypher queries | Agent decides what to retrieve |
| **Knows blast radius?** | No — vague estimates | Yes — exact named services | Yes + departments + escalation paths |
| **Who gets paged?** | Generic advice | Generic advice | `data-oncall` specifically |
| **Specialist knowledge?** | No | No | Yes — Kafka-specific runbooks |
| **LLM calls** | 1 | 1 | 2 (triage + specialist) |
| **Retrieval steps** | 1 | 3 | 4–5 |

> **Retrieval is not a fixed step. It's a decision made by the agent
> based on what it has already learned.**

---

## Workshop Guide

The full guided workshop is in [`WORKSHOP.md`](WORKSHOP.md) (~90 min, 4 parts).

**The progression:**

```
make rag kafka-broker        # Part 1: plain RAG — one search, one LLM
make graph-rag kafka-broker  # Part 2: add Neo4j topology queries
make tui kafka-broker        # Part 3: full agentic pipeline with live TUI
```

Run all three in separate tabs, compare outputs side by side. Each mode runs
the same incident so the differences are unambiguous.

---

## Quick Start

**Prerequisites:** [uv](https://docs.astral.sh/uv/), [Docker](https://www.docker.com/), [Ollama](https://ollama.com)

```bash
# 1. Pull models (one-time)
ollama pull gemma4:31b-cloud
ollama pull nomic-embed-text-v2-moe

# 2. Start stores, create .env, install deps
make setup

# 3. Seed 20 services into Qdrant (vector) + Neo4j (graph)
make seed

# 4. Run the full agentic pipeline
make tui kafka-broker
```

Verify both stores have data before running:

```bash
make inspect-mem    # lists all documents in Qdrant
make browse-graph   # opens Neo4j browser — run: MATCH (n) RETURN n
```

---

## Architecture

```
Incident
   │
   ├─ Plain RAG ──────────────── [Vector Search] ──────────────── [LLM] ── Response
   │
   ├─ Graph RAG ────── [Vector Search] ── [Neo4j: neighborhood] ──────────────────
   │                                      [Neo4j: blast radius] ── [LLM] ── Response
   │
   └─ Agentic RAG ── ┌─ Triage Agent ──────────────────────────┐
                     │  vector search + graph neighborhood      │
                     │  + blast radius + LLM classification     │
                     └─────────────────────┬───────────────────┘
                                           │ state: service, severity,
                                           │ blast_radius_report
                                           ▼
                              ┌─ Router Agent ─────────────────┐
                              │  reads affected_departments     │
                              │  routes to specialist           │
                              └────────────┬───────────────────┘
                                           │
                                           ▼
                              ┌─ Specialist [data] ────────────┐
                              │  targeted vector search         │
                              │  Kafka-expert system prompt     │
                              │  root cause + runbooks          │
                              └────────────────────────────────┘
```

**The "agentic" moment:** the router's decision reads `blast_radius_report.affected_departments`
from state — data retrieved by the triage agent from Neo4j. Retrieval *informs* routing,
which *determines* what gets retrieved next.

---

## Infrastructure Topology

20 services across 5 departments, seeded into both Qdrant and Neo4j from the
same source (`src/infrastructure/topology.py`):

```
platform:  api-gateway ─→ auth-service, config-service, service-mesh
data:      service-mesh ─→ postgres-primary, redis-cache, kafka-broker
product:   kafka-broker ─→ order-service, payment-service, notification-service
ml:        postgres-primary ─→ feature-store ─→ model-serving, experiment-tracker
infra:     k8s-controller ─→ monitoring-agent, ci-runner, dns-resolver
```

Adding a service to `topology.py` and re-seeding (`make seed`) automatically
updates both stores — no agent code changes required.

---

## Code Map

```
src/
├── infrastructure/
│   ├── topology.py          # 20 services, 5 departments — ground truth
│   ├── models.py            # Service, Incident, BlastRadiusReport, Severity
│   └── mock_apis.py         # incident templates
├── memory/
│   ├── config.py            # Mem0 + Neo4j driver setup
│   ├── graph.py             # seed/search Qdrant; neighborhood Cypher query
│   └── blast_radius.py      # DEPENDS_ON*1..4 traversal, severity estimation
├── agents/
│   ├── state.py             # TriageState (shared across all nodes)
│   ├── triage.py            # vector search + graph queries + LLM classify
│   ├── router.py            # reads blast_radius_report, picks specialist
│   ├── graph.py             # LangGraph: triage → router → specialist → END
│   └── specialists/         # platform, data, product, ml, infra
└── tui/
    ├── events.py            # emit() / register_handler() event bus
    ├── context.py           # thread-local current_node tracking
    └── display.py           # TriageTUI Rich live display

scripts/
├── run_plain_rag.py         # make rag
├── run_graph_rag.py         # make graph-rag
└── run_triage_tui.py        # make tui
```

Every event shown in the TUI corresponds to exactly one `emit()` call in the
memory or agent layer — traceable line by line.

---

## Configuration

`.env` file (created by `make setup` from `.env.example`):

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
make test      # pytest
make lint      # ruff
make check     # lint + test
make stop      # stop Docker services
make clean     # remove venv + volumes
```

See [`WORKSHOP.md`](WORKSHOP.md) for guided exercises and extension challenges.
