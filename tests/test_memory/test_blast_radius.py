from src.infrastructure.models import Severity
from src.memory.blast_radius import (
    compute_blast_radius,
    compute_upstream_blast_radius,
    estimate_severity,
)


class TestComputeBlastRadius:
    def test_given_root_service_when_compute_then_returns_deps(self):
        affected, paths, depts = compute_blast_radius("api-gateway")
        assert len(affected) == 0
        assert len(paths) == 0

    def test_given_order_service_when_compute_then_finds_downstream_deps(self):
        affected, paths, depts = compute_blast_radius("order-service")
        assert "api-gateway" in affected
        assert "postgres-primary" in affected
        assert "kafka-broker" in affected

    def test_given_deep_dependency_when_compute_then_finds_cascading(self):
        affected, paths, depts = compute_upstream_blast_radius("api-gateway")
        assert len(affected) > 0

    def test_given_multi_hop_when_compute_then_propagation_paths_long(self):
        affected, paths, depts = compute_blast_radius("order-service", max_hops=3)
        assert any(len(p) > 2 for p in paths)


class TestComputeUpstreamBlastRadius:
    def test_given_leaf_service_when_compute_upstream_then_few_affected(self):
        affected, paths, depts = compute_upstream_blast_radius("experiment-tracker")
        assert len(affected) == 0

    def test_given_central_service_when_compute_upstream_then_many_affected(self):
        affected, paths, depts = compute_upstream_blast_radius("api-gateway")
        assert len(affected) > 5

    def test_given_kafka_when_compute_upstream_then_cross_department(self):
        affected, paths, depts = compute_upstream_blast_radius("kafka-broker")
        dept_values = {d.value for d in depts}
        assert len(dept_values) > 1


class TestEstimateSeverity:
    def test_given_tier1_services_when_estimate_then_high(self):
        sev = estimate_severity(["order-service", "api-gateway"], [["a", "b", "c"]])
        assert sev in (Severity.HIGH, Severity.CRITICAL)

    def test_given_tier3_only_when_estimate_then_low(self):
        sev = estimate_severity(["training-pipeline"], [["a", "b"]])
        assert sev == Severity.LOW

    def test_given_empty_when_estimate_then_info(self):
        sev = estimate_severity([], [])
        assert sev == Severity.INFO
