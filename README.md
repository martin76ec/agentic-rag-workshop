# Agentic RAG Workshop

Build an infrastructure triage agent that uses **RAG (Retrieval-Augmented Generation)** with an **agentic workflow** to classify incidents, compute blast radius, and route to department specialists — all running locally with Ollama.

## What You'll Learn

- **Agentic RAG**: How agents use retrieved context to make decisions, not just answer questions
- **Memory as Knowledge Graph**: Using Mem0 to store and query infrastructure topology as vector memory
- **LangGraph Workflows**: Building stateful multi-step agent pipelines with conditional routing
- **Blast Radius Computation**: Graph traversal to predict cascading failures across services
- **Local-First Stack**: Everything runs on your machine — no API keys required

## Architecture

```
Incident → [Triage Agent] → [Router] → [Department Specialist]
               ↑                          ↑
          Mem0 Memory                 Mem0 Memory
         (topology +                  (department
          blast radius)                knowledge)
```

**Pipeline flow:**

1. **Triage** — LLM classifies the incident (service, severity, department) and enriches with Mem0 context
2. **Blast Radius** — BFS traversal of dependency graph to find affected services and departments
3. **Router** — Routes to the right department specialist, flags cross-department incidents
4. **Specialist** — Department expert provides root cause analysis, mitigation, and remediation

## Infrastructure Topology

20 services across 5 departments with real dependency chains:

```
api-gateway ──→ auth-service, config-service, service-mesh
service-mesh ──→ postgres-primary, redis-cache, kafka-broker, k8s-controller
kafka-broker ──→ order-service, payment-service, notification-service, training-pipeline
postgres-primary ──→ order-service, inventory-service, payment-service, feature-store, experiment-tracker
redis-cache ──→ inventory-service, feature-store
k8s-controller ──→ monitoring-agent, ci-runner, dns-resolver
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Docker](https://www.docker.com/) — for Qdrant vector store
- [Ollama](https://ollama.com/) — local LLM runtime

Install Ollama and pull the required models:

```bash
ollama pull gemma4:31b-cloud
ollama pull nomic-embed-text-v2-moe
```

## Quick Start

```bash
make setup     # Create venv, install deps, start Qdrant, create .env
make seed      # Load infrastructure topology into Mem0
make incident  # Run a random incident through the pipeline
```

Or specify a service:

```bash
make incident kafka-broker
```

## Manual Setup

If you prefer step-by-step:

```bash
# 1. Create environment
uv venv && uv sync

# 2. Start Qdrant
docker compose up -d qdrant

# 3. Configure (defaults work if Ollama is on localhost:11434)
cp .env.example .env

# 4. Seed infrastructure into Mem0
uv run python scripts/seed_infrastructure.py

# 5. Run an incident
uv run python scripts/run_incident.py
uv run python scripts/run_incident.py kafka-broker
```

## Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_LLM_MODEL` | `gemma4:31b-cloud` | LLM model for agent reasoning |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model for Mem0 |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `AGENTOPS_API_KEY` | _(empty)_ | Optional — AgentOps observability |
| `AGENTOPS_API_HOST` | `http://localhost:8000` | Optional — self-hosted AgentOps |

## Project Structure

```
src/
├── infrastructure/          # Domain models and mock data
│   ├── models.py            #   Service, Incident, BlastRadiusReport, etc.
│   ├── topology.py          #   20 services, 5 departments, dependency graph
│   └── mock_apis.py         #   Health checks, incident generation, metrics
├── memory/                  # Mem0 RAG layer
│   ├── config.py            #   Mem0 OSS config (Ollama LLM + embeddings, Qdrant)
│   ├── graph.py             #   Seed/search infrastructure in Mem0
│   └── blast_radius.py     #   BFS blast radius computation
├── agents/                  # LangGraph agent pipeline
│   ├── state.py             #   TriageState TypedDict
│   ├── triage.py            #   Triage node — LLM classification + Mem0 enrichment
│   ├── router.py            #   Router node — department routing + cross-dept flags
│   ├── graph.py             #   StateGraph: triage → router → specialist → END
│   └── specialists/         #   5 department specialist agents
│       ├── platform.py      #     API gateway, auth, config, mesh
│       ├── data.py          #     PostgreSQL, Redis, Kafka, ClickHouse
│       ├── product.py       #     Orders, inventory, payments, notifications
│       ├── ml.py            #     Feature store, model serving, training, experiments
│       └── infra.py         #     Kubernetes, monitoring, CI/CD, DNS
└── observability/           # AgentOps integration
    └── decorators.py        #   @agent, @operation, @tool, @trace

scripts/
├── seed_infrastructure.py   # Load topology into Mem0 (Rich output)
├── run_incident.py           # Run incident through pipeline (Rich output)
└── setup_dev.sh             # Dev environment bootstrap

tests/                       # 58 tests (pytest)
```

## How It Works

### 1. Infrastructure as Memory

The 20-service topology is seeded into Mem0 as vector memory with structured metadata:

```python
memory.add(
    "Service: kafka-broker. Department: data. Tier: 1. Depends on: service-mesh...",
    user_id="infrastructure",
    metadata={"type": "service", "service_name": "kafka-broker", "department": "data", "tier": "1"},
    infer=False,
)
```

Agents query this memory to retrieve context about affected services during triage.

### 2. Triage with RAG

The triage agent:
1. Sends the incident to the LLM for classification (service, severity, department)
2. Queries Mem0 for context about the classified service
3. Computes blast radius via BFS on the dependency graph
4. Returns enriched classification with memory context

### 3. Blast Radius

Graph traversal finds both **upstream** (services that depend on the affected one) and **downstream** (services the affected one depends on) impact:

```python
compute_blast_radius("kafka-broker", max_hops=4)
# → affected: [service-mesh], departments: [data, product, ml], severity: HIGH
```

### 4. Specialist Agents

Each department specialist has domain expertise (system prompts) and queries Mem0 for department-specific knowledge before providing analysis.

## Workshop Challenges

After running the basic pipeline, try these extensions:

### Easy
- **Add a new department**: Create a `security` department with services like `waf-proxy` and `vault`, wire it into the topology, router, and specialist coordinator
- **Custom incident templates**: Add new incident templates to `mock_apis.py` for your department's services

### Medium
- **Auto-remediation**: Add a remediation node after the specialist that suggests and simulates corrective actions (e.g., restart pod, scale replicas, failover)
- **Learning loop**: After each incident, store the specialist's analysis back into Mem0 so future triages can reference past resolutions

### Hard
- **Multi-agent correlation**: When multiple incidents arrive simultaneously, build a correlation agent that detects related incidents (e.g., kafka-broker latency + order-service errors) and creates a unified response
- **Replace deterministic blast radius with LLM reasoning**: Instead of BFS traversal, let the LLM reason about cascading failures from Mem0 context alone — compare accuracy
- **Human-in-the-loop**: Add a LangGraph interrupt node that pauses the pipeline and asks the operator for confirmation before executing remediation

## Development

```bash
make test      # Run 58 tests
make lint      # Ruff check
make check     # Lint + test
make clean     # Remove venv, caches, Qdrant data
make status    # Check if Qdrant is running
```

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| LLM | Ollama (Gemma 4) | Local, no API keys, self-hosted |
| Embeddings | Ollama (nomic-embed-text-v2) | Local, same server |
| Vector Store | Qdrant | OSS, fast, Docker-friendly |
| Memory | Mem0 OSS | Structured memory with metadata filters |
| Agent Framework | LangGraph | Stateful graph-based workflows |
| Observability | AgentOps | Optional tracing dashboard |