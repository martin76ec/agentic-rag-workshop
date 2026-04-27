from src.infrastructure.mock_apis import (
    generate_all_health_checks,
    generate_health_check,
    generate_incident,
    generate_metrics,
)
from src.infrastructure.models import HealthStatus, Severity


class TestGenerateHealthCheck:
    def test_given_service_name_when_generate_health_then_returns_result(self):
        result = generate_health_check("api-gateway")
        assert result.service_name == "api-gateway"
        assert result.status in list(HealthStatus)

    def test_given_force_down_when_generate_health_then_status_down(self):
        result = generate_health_check("kafka-broker", force_status=HealthStatus.DOWN)
        assert result.status == HealthStatus.DOWN
        assert result.error_rate > 0.5

    def test_given_force_healthy_when_generate_health_then_status_healthy(self):
        result = generate_health_check("redis-cache", force_status=HealthStatus.HEALTHY)
        assert result.status == HealthStatus.HEALTHY
        assert result.latency_ms < 100

    def test_given_nonexistent_service_when_generate_health_then_unknown(self):
        result = generate_health_check("nonexistent")
        assert result.status == HealthStatus.UNKNOWN


class TestGenerateAllHealthChecks:
    def test_given_no_args_when_generate_all_then_returns_all_services(self):
        results = generate_all_health_checks()
        assert len(results) == 20

    def test_given_force_down_list_when_generate_all_then_those_services_down(self):
        results = generate_all_health_checks(force_down=["postgres-primary", "redis-cache"])
        down_services = [r for r in results if r.status == HealthStatus.DOWN]
        down_names = {r.service_name for r in down_services}
        assert "postgres-primary" in down_names
        assert "redis-cache" in down_names


class TestGenerateIncident:
    def test_given_service_when_generate_incident_then_returns_incident(self):
        incident = generate_incident("api-gateway")
        assert incident.service_name == "api-gateway"
        assert incident.severity in list(Severity)
        assert incident.incident_id.startswith("INC-")
        assert len(incident.symptoms) > 0

    def test_given_template_index_when_generate_incident_then_uses_template(self):
        incident = generate_incident("auth-service", template_index=0)
        assert "latency" in incident.description.lower()

    def test_given_nonexistent_service_when_generate_incident_then_raises(self):
        import pytest
        with pytest.raises(ValueError):
            generate_incident("nonexistent")


class TestGenerateMetrics:
    def test_given_service_when_generate_metrics_then_returns_points(self):
        points = generate_metrics("kafka-broker", count=3)
        assert len(points) == 18
        assert all(p.service_name == "kafka-broker" for p in points)

    def test_given_metrics_then_various_metric_types_present(self):
        points = generate_metrics("api-gateway", count=1)
        metric_names = {p.metric for p in points}
        assert "cpu_percent" in metric_names
        assert "latency_p99" in metric_names
