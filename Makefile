.PHONY: setup dev seed incident test lint check clean help exercise verify solution eval

# Extract a positional argument (e.g. "1.1" from "make exercise 1.1") and
# squash it into a no-op target so make doesn't complain.
EX_NUM := $(strip $(filter-out exercise verify solution,$(MAKECMDGOALS)))
EX_PART := $(word 1,$(subst ., ,$(EX_NUM)))
EX_DIR  := $(if $(filter 1,$(EX_PART)),part1_plain,$(if $(filter 2,$(EX_PART)),part2_graph,$(if $(filter 3,$(EX_PART)),part3_agentic,)))

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: ## Full dev setup (venv + deps + Qdrant + Neo4j + .env)
	uv venv && uv sync
	docker compose up -d qdrant neo4j
	@echo "Waiting for Qdrant..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:6333/healthz | grep -q ok; then echo "Qdrant ready!"; break; fi; \
		sleep 1; \
	done
	@echo "Waiting for Neo4j..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:7474 > /dev/null 2>&1; then echo "Neo4j ready!"; break; fi; \
		sleep 2; \
	done
	@test -f .env || cp .env.example .env

dev: ## Start Qdrant and Neo4j in background
	docker compose up -d qdrant neo4j

browse-graph: ## Open Neo4j browser UI
	open http://localhost:7474

seed: ## Seed infrastructure topology into Mem0
	uv run python scripts/seed_infrastructure.py

inspect-mem: ## Show all documents stored in Mem0/Qdrant
	uv run python scripts/inspect_mem.py

incident: ## Run incident triage (optionally pass SERVICE=name)
	uv run python scripts/run_incident.py $(filter-out $@,$(MAKECMDGOALS))

# ── Workshop progression (Track B — compare it) ─────────────────────────────
rag: ## [Track B] Plain RAG — vector + single LLM (SERVICE=name)
	uv run python scripts/run_plain_rag.py $(filter-out $@,$(MAKECMDGOALS))

graph-rag: ## [Track B] Graph RAG — vector + Neo4j + single LLM (SERVICE=name)
	uv run python scripts/run_graph_rag.py $(filter-out $@,$(MAKECMDGOALS))

tui: ## [Track B] Agentic RAG — full multi-agent pipeline with live TUI (SERVICE=name)
	uv run python scripts/run_triage_tui.py $(filter-out $@,$(MAKECMDGOALS))

# ── Track A — build it (broken-code exercises) ──────────────────────────────
exercise: ## [Track A] Run a broken exercise (e.g. make exercise 1.1)
	@test -n "$(EX_NUM)" || (echo "Usage: make exercise N.M  (e.g. make exercise 1.1)" && exit 1)
	@test -n "$(EX_DIR)" || (echo "Unknown part '$(EX_PART)'. Use 1, 2, or 3." && exit 1)
	@echo ""
	@echo "═══ Exercise $(EX_NUM) — $(EX_DIR) ═══"
	@echo ""
	@awk '/^## Las /{flag=1;print;next} /^## [^L]/{flag=0} flag' exercises/$(EX_DIR)/README.md
	@echo ""
	@echo "─── Running tests on the broken code ───"
	@uv run pytest exercises/$(EX_DIR)/tests.py -v --tb=short || true
	@echo ""
	@echo "Edit the .py file with TODOs in exercises/$(EX_DIR)/. The README maps each fix # to its file."
	@echo "Pistas: exercises/$(EX_DIR)/hints.md"

verify: ## [Track A] Run only the tests for an exercise (e.g. make verify 1.1)
	@test -n "$(EX_NUM)" || (echo "Usage: make verify N.M" && exit 1)
	@test -n "$(EX_DIR)" || (echo "Unknown part '$(EX_PART)'." && exit 1)
	uv run pytest exercises/$(EX_DIR)/tests.py -v

solution: ## [Track A] Reveal the reference solution for an exercise
	@test -n "$(EX_NUM)" || (echo "Usage: make solution N.M" && exit 1)
	@case "$(EX_NUM)" in \
		1.1) echo "Reference: src/memory/graph.py :: service_to_memory_content (note: monolithic in src/, your sectioned version is the educational one)" ;; \
		1.2) echo "Reference: src/memory/graph.py :: search_services" ;; \
		1.3) echo "Reference: src/agents/triage.py — see how the prompt is composed" ;; \
		2.1) echo "Reference: src/memory/graph.py :: _NEIGHBORHOOD_CYPHER" ;; \
		2.2) echo "Reference: src/memory/blast_radius.py :: _BLAST_CYPHER" ;; \
		2.3) echo "Reference: src/agents/triage.py — graph context block (lines 95-105)" ;; \
		3.1) echo "Reference: src/agents/triage.py :: triage_node — JSON parsing block" ;; \
		3.2) echo "Reference: src/agents/router.py :: router_node" ;; \
		3.3) echo "Reference: src/agents/state.py :: TriageState" ;; \
		3.4) echo "Reference: src/agents/specialists/data.py :: DATA_SYSTEM_PROMPT" ;; \
		*)   echo "No reference mapped for $(EX_NUM)" ;; \
	esac

# ── Evaluation ──────────────────────────────────────────────────────────────
eval: ## Run retrieval-quality evaluation on the gold set (MODE=vector|graph K=5)
	uv run python -m eval.run_eval --mode $${MODE:-vector} --k $${K:-5}

# ── Quality gates ───────────────────────────────────────────────────────────
test: ## Run the project test suite (excludes broken Track A exercises)
	uv run pytest tests/ -v

test-exercises: ## Run Track A exercise tests (most fail until you fix the TODOs)
	uv run pytest exercises/ -v

lint: ## Lint with ruff
	uv run ruff check src/ tests/ exercises/ eval/

check: lint test ## Lint + test

clean: ## Remove venv, caches, Qdrant data
	rm -rf .venv .pytest_cache .ruff_cache __pycache__
	docker compose down -v

stop: ## Stop Qdrant + Neo4j
	docker compose down

status: ## Check Qdrant health
	@curl -s http://localhost:6333/healthz || echo "Qdrant not running"

# Catch-all for positional args (e.g. "1.1" in "make exercise 1.1")
%:
	@:
