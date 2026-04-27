from src.infrastructure.topology import get_service_by_name
from src.memory.graph import service_to_memory_content, service_to_metadata


class TestServiceToMemoryContent:
    def test_given_service_when_convert_then_content_includes_name_and_department(self):
        service = get_service_by_name("kafka-broker")
        content = service_to_memory_content(service)
        assert "kafka-broker" in content
        assert "data" in content
        assert "Tier" in content

    def test_given_service_with_deps_when_convert_then_content_includes_deps(self):
        service = get_service_by_name("order-service")
        content = service_to_memory_content(service)
        assert "Depends on:" in content
        assert "api-gateway" in content

    def test_given_root_service_when_convert_then_depends_on_none(self):
        service = get_service_by_name("api-gateway")
        content = service_to_memory_content(service)
        assert "none" in content


class TestServiceToMetadata:
    def test_given_service_when_convert_then_metadata_has_type(self):
        service = get_service_by_name("redis-cache")
        metadata = service_to_metadata(service)
        assert metadata["type"] == "service"
        assert metadata["service_name"] == "redis-cache"
        assert metadata["department"] == "data"

    def test_given_service_with_dependents_when_convert_then_metadata_has_dependents(self):
        service = get_service_by_name("api-gateway")
        metadata = service_to_metadata(service)
        assert metadata["dependents"] != ""

    def test_given_service_when_convert_then_depends_on_joined(self):
        service = get_service_by_name("order-service")
        metadata = service_to_metadata(service)
        assert "api-gateway" in metadata["depends_on"]
        assert "postgres-primary" in metadata["depends_on"]
