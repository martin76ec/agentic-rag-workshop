#!/bin/bash
set -euo pipefail

echo "=== Agentic RAG Workshop — Dev Setup ==="

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed. Install Docker Desktop first."
    exit 1
fi

echo "1. Creating virtual environment..."
uv venv
source .venv/bin/activate

echo "2. Installing dependencies..."
uv sync

echo "3. Starting Qdrant (Docker)..."
docker compose up -d qdrant
echo "   Waiting for Qdrant to be healthy..."
for i in $(seq 1 30); do
    if curl -s http://localhost:6333/healthz | grep -q "ok"; then
        echo "   Qdrant is healthy!"
        break
    fi
    sleep 1
done

if [ ! -f .env ]; then
    echo "4. Creating .env from .env.example..."
    cp .env.example .env
    echo "   EDIT .env to configure Ollama models before proceeding!"
else
    echo "4. .env already exists, skipping..."
fi

echo ""
echo "=== Setup Complete ==="
echo "Next steps:"
    echo "  1. Edit .env to configure Ollama models (if not using defaults)"
echo "  2. Seed infrastructure: uv run python scripts/seed_infrastructure.py"
echo "  3. Run an incident:    uv run python scripts/run_incident.py"
echo "  4. Or specify service: uv run python scripts/run_incident.py kafka-broker"