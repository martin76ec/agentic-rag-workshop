"""
Tests for src.memory.blast_radius.

Pure helpers (estimate_severity) run anywhere. Cypher-backed helpers
(_cypher_blast_radius, generate_blast_radius_report) require a live Neo4j
and are skipped when one isn't available.
"""
import os

import pytest

from src.infrastructure.models import Severity
from src.memory.blast_radius import (
    _cypher_blast_radius,
    estimate_severity,
    generate_blast_radius_report,
)


def _neo4j_available() -> bool:
    if os.environ.get("SKIP_NEO4J_TESTS"):
        return False
    try:
        from src.memory.config import get_neo4j_driver
        driver = get_neo4j_driver()
        try:
            with driver.session() as session:
                session.run("RETURN 1").consume()
        finally:
            driver.close()
        return True
    except Exception:
        return False


needs_neo4j = pytest.mark.skipif(
    not _neo4j_available(),
    reason="Neo4j is not running (start with `make dev` and `make seed`).",
)


class TestEstimateSeverity:
    def test_tier1_services_with_long_paths_is_high_or_critical(self):
        sev = estimate_severity(
            ["order-service", "api-gateway"],
            [["api-gateway", "order-service", "postgres-primary"]],
        )
        assert sev in (Severity.HIGH, Severity.CRITICAL)

    def test_tier3_only_is_low(self):
        sev = estimate_severity(["training-pipeline"], [["training-pipeline", "k8s-controller"]])
        assert sev == Severity.LOW

    def test_empty_is_info(self):
        assert estimate_severity([], []) == Severity.INFO

    def test_unknown_service_is_info(self):
        assert estimate_severity(["nonexistent-service"], []) == Severity.INFO


@needs_neo4j
class TestCypherBlastRadius:
    def test_kafka_broker_has_cross_department_blast(self):
        affected, paths, depts = _cypher_blast_radius("kafka-broker")
        assert len(affected) > 0
        assert len({d.value for d in depts}) > 1

    def test_max_hops_caps_traversal(self):
        deep, _, _ = _cypher_blast_radius("kafka-broker", max_hops=4)
        shallow, _, _ = _cypher_blast_radius("kafka-broker", max_hops=1)
        assert len(deep) >= len(shallow)


@needs_neo4j
class TestGenerateBlastRadiusReport:
    def test_report_for_kafka_includes_root_metadata(self):
        report = generate_blast_radius_report("kafka-broker", incident_id="TEST-1")
        assert report.incident_id == "TEST-1"
        assert report.root_service == "kafka-broker"
        assert report.estimated_impact in Severity
