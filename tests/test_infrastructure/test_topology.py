from src.infrastructure.models import Department
from src.infrastructure.topology import (
    DEPENDENCIES,
    SERVICES,
    get_dependencies,
    get_dependents,
    get_service_by_name,
    get_services_by_department,
)


class TestTopologyData:
    def test_given_topology_when_loaded_then_has_20_services(self):
        assert len(SERVICES) == 20

    def test_given_topology_when_loaded_then_all_departments_present(self):
        departments = {s.department for s in SERVICES}
        assert Department.PLATFORM in departments
        assert Department.DATA in departments
        assert Department.PRODUCT in departments
        assert Department.ML in departments
        assert Department.INFRA in departments

    def test_given_topology_when_loaded_then_dependencies_match_services(self):
        service_names = {s.name for s in SERVICES}
        for dep in DEPENDENCIES:
            assert dep.source in service_names
            assert dep.target in service_names


class TestGetServiceByName:
    def test_given_existing_name_when_lookup_then_returns_service(self):
        service = get_service_by_name("kafka-broker")
        assert service is not None
        assert service.name == "kafka-broker"
        assert service.department == Department.DATA

    def test_given_nonexistent_name_when_lookup_then_returns_none(self):
        assert get_service_by_name("nonexistent-service") is None


class TestGetServicesByDepartment:
    def test_given_platform_dept_when_filter_then_returns_platform_services(self):
        services = get_services_by_department(Department.PLATFORM)
        assert len(services) == 4
        assert all(s.department == Department.PLATFORM for s in services)

    def test_given_ml_dept_when_filter_then_returns_ml_services(self):
        services = get_services_by_department(Department.ML)
        assert len(services) == 4
        assert all(s.department == Department.ML for s in services)


class TestGetDependents:
    def test_given_api_gateway_when_get_dependents_then_returns_services_that_depend_on_it(self):
        dependents = get_dependents("api-gateway")
        dependent_names = {s.name for s in dependents}
        assert "auth-service" in dependent_names
        assert "order-service" in dependent_names

    def test_given_leaf_service_when_get_dependents_then_returns_its_consumers(self):
        dependents = get_dependents("clickhouse-analytics")
        assert len(dependents) > 0


class TestGetDependencies:
    def test_given_order_service_when_get_dependencies_then_returns_its_deps(self):
        deps = get_dependencies("order-service")
        dep_names = {s.name for s in deps}
        assert "api-gateway" in dep_names
        assert "postgres-primary" in dep_names
        assert "kafka-broker" in dep_names

    def test_given_root_service_when_get_dependencies_then_returns_empty(self):
        deps = get_dependencies("api-gateway")
        assert len(deps) == 0
