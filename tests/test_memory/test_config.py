from unittest.mock import MagicMock, patch

from src.memory.config import COLLECTION_NAME


class TestMem0Config:
    def test_given_default_config_when_get_collection_name_then_is_infrastructure(self):
        assert COLLECTION_NAME == "infrastructure_topology"

    def test_given_env_vars_when_get_memory_then_config_passed_to_mem0(self):
        import os

        original_host = os.environ.get("QDRANT_HOST")
        original_port = os.environ.get("QDRANT_PORT")

        os.environ["QDRANT_HOST"] = "test-host"
        os.environ["QDRANT_PORT"] = "9999"

        try:
            with patch("src.memory.config.Memory") as mock_memory_cls:
                mock_instance = MagicMock()
                mock_memory_cls.from_config.return_value = mock_instance

                from src.memory.config import get_memory
                get_memory()

                call_args = mock_memory_cls.from_config.call_args
                config = call_args[0][0]
                assert config["vector_store"]["config"]["host"] == "test-host"
                assert config["vector_store"]["config"]["port"] == 9999
        finally:
            if original_host is not None:
                os.environ["QDRANT_HOST"] = original_host
            else:
                os.environ.pop("QDRANT_HOST", None)
            if original_port is not None:
                os.environ["QDRANT_PORT"] = original_port
            else:
                os.environ.pop("QDRANT_PORT", None)
