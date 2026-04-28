"""
Tests for Exercise 1 — Plain RAG.

Run with:  uv run pytest exercises/part1_plain/tests.py -v
Or via:    make check 1.1   |   make check 1.2   |   make check 1.3
"""
from unittest.mock import MagicMock

import pytest

from exercises.part1_plain import chunking, prompt, search
from src.infrastructure.models import Department, Service


@pytest.fixture
def kafka() -> Service:
    return Service(
        name="kafka-broker",
        department=Department.DATA,
        description="Event backbone for async messaging across services.",
        tier=1,
        region="us-east-1",
        depends_on=["k8s-controller"],
        sla_minutes=4.32,
        tags=["streaming", "tier1", "data"],
        metadata={"port": 9092, "protocol": "tcp"},
    )


# ── 1.1  chunking ──────────────────────────────────────────────────────────

class TestChunking:
    def test_returns_multiple_chunks(self, kafka: Service):
        chunks = chunking.chunk_service(kafka)
        assert len(chunks) >= 3, (
            "Expected at least 3 sectioned chunks per service. "
            "One mega-chunk is the broken baseline."
        )

    def test_chunks_are_focused(self, kafka: Service):
        chunks = chunking.chunk_service(kafka)
        # No chunk should be longer than ~200 chars; tight chunks → focused embeddings.
        assert max(len(c) for c in chunks) <= 200, (
            "Chunks are too long — split by aspect (identity / deps / ops / dept)."
        )

    def test_each_chunk_mentions_the_service(self, kafka: Service):
        chunks = chunking.chunk_service(kafka)
        assert all("kafka-broker" in c for c in chunks), (
            "Every chunk should still mention the service name so retrieval can "
            "associate it back."
        )


# ── 1.2  search ────────────────────────────────────────────────────────────

class TestSearch:
    def _fake_memory(self, results: list[dict]) -> MagicMock:
        mem = MagicMock()
        mem.search.return_value = {"results": results}
        return mem

    def test_top_k_is_increased(self):
        mem = self._fake_memory([])
        search.search(mem, "kafka is down")
        call_kwargs = mem.search.call_args.kwargs
        assert call_kwargs.get("top_k", 1) >= 3, "top_k must be >= 3"

    def test_filters_by_user_id(self):
        mem = self._fake_memory([])
        search.search(mem, "kafka is down")
        call_kwargs = mem.search.call_args.kwargs
        filters = call_kwargs.get("filters") or {}
        assert filters.get("user_id") == "infrastructure", (
            "Pass filters={'user_id': 'infrastructure'} to memory.search()."
        )

    def test_drops_non_service_entries(self):
        mem = self._fake_memory([
            {
                "memory": "kafka is the event backbone",
                "metadata": {"type": "service", "service_name": "kafka-broker", "department": "data"},
            },
            {
                "memory": "data team owns kafka",
                "metadata": {"type": "department_knowledge", "department": "data"},
            },
        ])
        hits = search.search(mem, "kafka")
        assert all(h["metadata"]["type"] == "service" for h in hits), (
            "Department-knowledge entries should not appear in service results."
        )
        assert len(hits) == 1

    def test_department_filter(self):
        mem = self._fake_memory([
            {
                "memory": "kafka",
                "metadata": {"type": "service", "service_name": "kafka-broker", "department": "data"},
            },
            {
                "memory": "api-gateway",
                "metadata": {"type": "service", "service_name": "api-gateway", "department": "platform"},
            },
        ])
        hits = search.search(mem, "anything", department="data")
        assert len(hits) == 1
        assert hits[0]["metadata"]["service_name"] == "kafka-broker"


# ── 1.3  prompt ────────────────────────────────────────────────────────────

class TestPrompt:
    def test_prompt_includes_query(self):
        out = prompt.build_prompt("kafka-broker is returning 5xx", [])
        assert "kafka-broker is returning 5xx" in out

    def test_prompt_includes_retrieved_context(self):
        hits = [
            {"memory": "kafka-broker is the event backbone for async messaging.",
             "metadata": {"service_name": "kafka-broker", "department": "data", "tier": "1"}},
        ]
        out = prompt.build_prompt("Kafka down?", hits)
        assert "event backbone" in out, (
            "The retrieved chunk's text MUST appear in the assembled prompt. "
            "Otherwise the LLM has no grounding."
        )

    def test_prompt_handles_empty_hits(self):
        out = prompt.build_prompt("Kafka down?", [])
        # Must still be a usable string and contain the query.
        assert isinstance(out, str)
        assert "Kafka down?" in out
