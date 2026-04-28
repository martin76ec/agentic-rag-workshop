"""
Tests for Exercise 2 — Graph RAG.

Run with:  uv run pytest exercises/part2_graph/tests.py -v
"""
from pathlib import Path

import pytest

from exercises.part2_graph import blast_radius, fusion

# ── 2.1  neighborhood Cypher ────────────────────────────────────────────────

class TestNeighborhood:
    @pytest.fixture
    def cypher_text(self) -> str:
        return (Path(__file__).parent / "neighborhood.cypher").read_text()

    def test_walks_outbound_edges(self, cypher_text: str):
        assert "(s)-[:DEPENDS_ON]->(dep" in cypher_text.replace(" ", ""), (
            "Add an OPTIONAL MATCH that walks outbound DEPENDS_ON edges."
        )

    def test_walks_inbound_edges(self, cypher_text: str):
        assert "(aff:Service)-[:DEPENDS_ON]->(s)".replace(" ", "") in cypher_text.replace(" ", ""), (
            "Add an OPTIONAL MATCH that walks inbound DEPENDS_ON edges."
        )

    def test_collects_dependencies(self, cypher_text: str):
        assert "collect(DISTINCT dep.name)" in cypher_text.replace(" ", "").replace("\n", "")
        assert "collect(DISTINCT aff.name)" in cypher_text.replace(" ", "").replace("\n", "")


# ── 2.2  blast radius (variable-length paths) ───────────────────────────────

class TestBlastRadius:
    def test_uses_variable_length_pattern(self):
        cypher = blast_radius.blast_radius_cypher(max_hops=4)
        assert "*1.." in cypher.replace(" ", ""), (
            "Use a variable-length path  -[:DEPENDS_ON*1..N]->  to find transitive dependents."
        )

    def test_respects_max_hops(self):
        cypher_4 = blast_radius.blast_radius_cypher(max_hops=4)
        cypher_2 = blast_radius.blast_radius_cypher(max_hops=2)
        assert "*1..4" in cypher_4.replace(" ", "")
        assert "*1..2" in cypher_2.replace(" ", "")

    def test_returns_path_nodes(self):
        cypher = blast_radius.blast_radius_cypher()
        assert "path_nodes" in cypher, "Return the cascade path so callers can show the chain."
        assert "nodes(path)" in cypher.replace(" ", ""), (
            "Bind the pattern to a `path` variable and return [n IN nodes(path) | n.name]."
        )


# ── 2.3  fusion ─────────────────────────────────────────────────────────────

class TestFusion:
    @pytest.fixture
    def sample(self) -> dict:
        return {
            "query": "kafka-broker is returning 5xx",
            "vector_hits": [
                {"memory": "kafka-broker is the event backbone.",
                 "metadata": {"service_name": "kafka-broker", "department": "data", "tier": "1"}},
            ],
            "neighborhood": {
                "tier": 1,
                "department": "data",
                "depends_on": ["k8s-controller"],
                "depended_by": ["clickhouse-analytics", "order-service", "payment-service"],
            },
            "blast_paths": [
                ["kafka-broker", "clickhouse-analytics", "experiment-tracker"],
                ["kafka-broker", "order-service"],
            ],
            "affected_services": ["clickhouse-analytics", "experiment-tracker", "order-service"],
        }

    def test_topology_section_appears(self, sample):
        out = fusion.fuse_context(**sample)
        assert "Topology" in out or "topology" in out, "Render a topology section."
        assert "k8s-controller" in out, "Topology should list direct dependencies."

    def test_cascade_paths_rendered_as_arrows(self, sample):
        out = fusion.fuse_context(**sample)
        assert "kafka-broker → clickhouse-analytics → experiment-tracker" in out, (
            "Render each cascade path as an arrow chain."
        )

    def test_supporting_chunks_included(self, sample):
        out = fusion.fuse_context(**sample)
        assert "event backbone" in out

    def test_priority_order(self, sample):
        out = fusion.fuse_context(**sample)
        topo_idx = max(out.find("Topology"), out.find("topology"))
        casc_idx = out.find("kafka-broker → clickhouse-analytics")
        supp_idx = out.find("event backbone")
        q_idx    = out.find(sample["query"])
        assert topo_idx >= 0 < casc_idx, "Topology and cascade sections must appear."
        assert topo_idx < casc_idx < supp_idx < q_idx, (
            "Priority order should be: topology → cascade → supporting → question."
        )

    def test_dict_repr_not_dumped(self, sample):
        out = fusion.fuse_context(**sample)
        assert "{'depends_on'" not in out, (
            "Don't dump dicts into the prompt — render structured bullets."
        )
