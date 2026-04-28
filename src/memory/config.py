import os

from mem0 import Memory
from neo4j import Driver, GraphDatabase

COLLECTION_NAME = "infrastructure_topology"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "gemma4:31b-cloud")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text-v2-moe:latest")
OLLAMA_EMBEDDING_DIMS = int(os.getenv("OLLAMA_EMBEDDING_DIMS", "768"))

NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def get_memory() -> Memory:
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": COLLECTION_NAME,
                "host": qdrant_host,
                "port": qdrant_port,
                "embedding_model_dims": OLLAMA_EMBEDDING_DIMS,
            },
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": OLLAMA_LLM_MODEL,
                "ollama_base_url": OLLAMA_BASE_URL,
                "temperature": 0.1,
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": OLLAMA_EMBEDDING_MODEL,
                "ollama_base_url": OLLAMA_BASE_URL,
                "embedding_dims": OLLAMA_EMBEDDING_DIMS,
            },
        },
        "version": "v1.1",
    }

    return Memory.from_config(config)


def get_neo4j_driver() -> Driver:
    return GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
