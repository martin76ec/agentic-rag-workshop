import pytest

from src.infrastructure.models import (
    Department,
    Dependency,
    Incident,
    Service,
    Severity,
)


class TestServiceModel:
    def test_given_valid_data_when_create_service_then_fields_populated(self):
        service = Service(
            name="test-svc",
            department=Department.PLATFORM,
            description="A test service",
            tier=1,
            depends_on=["api-gateway"],
            sla_minutes=4.38,
        )
        assert service.name == "test-svc"
        assert service.department == Department.PLATFORM
        assert service.tier == 1
        assert service.depends_on == ["api-gateway"]

    def test_given_tier_out_of_range_when_create_service_then_validation_error(self):
        with pytest.raises(Exception):
            Service(
                name="bad-svc",
                department=Department.PLATFORM,
                description="Bad tier",
                tier=5,
                sla_minutes=10.0,
            )

    def test_given_metadata_with_alias_when_create_service_then_metadata_accessible(self):
        service = Service(
            name="test-svc",
            department=Department.DATA,
            description="Test",
            tier=2,
            sla_minutes=26.28,
            metadata={"port": 8080},
        )
        assert service.metadata_ == {"port": 8080}


class TestIncidentModel:
    def test_given_valid_data_when_create_incident_then_fields_populated(self):
        incident = Incident(
            incident_id="INC-001",
            service_name="kafka-broker",
            severity=Severity.CRITICAL,
            description="Kafka is down",
            symptoms=["crash_loop", "no_messages"],
        )
        assert incident.incident_id == "INC-001"
        assert incident.severity == Severity.CRITICAL

    def test_given_default_fields_when_create_incident_then_lists_empty(self):
        incident = Incident(
            incident_id="INC-002",
            service_name="redis-cache",
            severity=Severity.HIGH,
            description="Redis OOM",
        )
        assert incident.symptoms == []
        assert incident.metadata_ == {}


class TestDependencyModel:
    def test_given_source_and_target_when_create_dependency_then_fields_correct(self):
        dep = Dependency(source="order-service", target="postgres-primary", critical=True)
        assert dep.source == "order-service"
        assert dep.target == "postgres-primary"
        assert dep.critical is True

    def test_given_default_critical_when_create_dependency_then_true(self):
        dep = Dependency(source="test-svc", target="other-svc")
        assert dep.critical is True
