.PHONY: setup dev seed incident test lint check clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Full dev setup (venv + deps + Qdrant + .env)
	uv venv && uv sync
	docker compose up -d qdrant
	@echo "Waiting for Qdrant..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:6333/healthz | grep -q ok; then echo "Qdrant ready!"; break; fi; \
		sleep 1; \
	done
	@test -f .env || cp .env.example .env

dev: ## Start Qdrant in background
	docker compose up -d qdrant

seed: ## Seed infrastructure topology into Mem0
	uv run python scripts/seed_infrastructure.py

incident: ## Run incident triage (optionally pass SERVICE=name)
	uv run python scripts/run_incident.py $(filter-out $@,$(MAKECMDGOALS))

test: ## Run all tests
	uv run pytest tests/ -v

lint: ## Lint with ruff
	uv run ruff check src/ tests/

check: lint test ## Lint + test

clean: ## Remove venv, caches, Qdrant data
	rm -rf .venv .pytest_cache .ruff_cache __pycache__
	docker compose down -v

stop: ## Stop Qdrant
	docker compose down

status: ## Check Qdrant health
	@curl -s http://localhost:6333/healthz || echo "Qdrant not running"

%:
	@: