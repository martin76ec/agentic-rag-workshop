"""
Exercise 1.1 — Chunking
========================
Right now every service serializes into ONE giant chunk that mixes
description, dependencies, tags, SLA, and metadata into a single string.
That's terrible for retrieval: the embedding tries to mean everything at once,
and "what depends on Kafka?" matches as poorly as "who owns Redis?".

Your job: produce SECTIONED chunks per service so the embedder learns
narrower meanings. Aim for 3–5 chunks per service, each ~50–120 chars.

The reference implementation lives in src/memory/graph.py
(`service_to_memory_content`). Don't peek until you've tried.
"""
from src.infrastructure.models import Service


def chunk_service(service: Service) -> list[str]:
    """Return a list of small text chunks for a single service.

    Each chunk should focus on ONE aspect (identity, dependencies, ops, etc.)
    so vector search can match a query to the right facet.

    Returned chunks are inserted into Qdrant individually; metadata is added
    by the caller.
    """
    # TODO 1.1.a — replace this single-chunk fallback with sectioned chunks.
    # Hint: think about what queries the on-call engineer will type.
    #   - "what does kafka-broker do?"             (identity / description)
    #   - "what depends on kafka-broker?"          (dependents)
    #   - "kafka-broker SLA"                       (ops/SLA)
    #   - "data services owned by kafka team"      (department)
    # Each of those questions should match a different chunk.
    return [
        f"{service.name} {service.department.value} tier{service.tier} "
        f"{service.description} depends_on={','.join(service.depends_on)} "
        f"tags={','.join(service.tags)} sla={service.sla_minutes}m"
    ]
