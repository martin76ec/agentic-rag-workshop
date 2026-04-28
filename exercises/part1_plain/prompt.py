"""
Exercise 1.3 — Prompt construction
==================================
The system prompt promises to "use the retrieved context" but never actually
inserts it into the user message. The LLM is asked to reason about Kafka
without ever being shown what we retrieved about Kafka. Output is generic.

Fix: build a prompt that ACTUALLY includes the retrieved chunks, with
clear delimiters and one-shot framing for severity classification.
"""
from typing import Any

SYSTEM_PROMPT = (
    "You are an infrastructure on-call assistant. Use the retrieved context "
    "to answer concretely — name the affected services, the cascade path, "
    "and concrete mitigation steps. If the context is empty, say so."
)


def build_prompt(query: str, hits: list[dict[str, Any]]) -> str:
    """Compose the user message that the LLM will see.

    Args:
        query: free-text question from the on-call engineer.
        hits:  list of search hits (from exercise 1.2).

    Returns:
        A single string that contains the query AND the retrieved context,
        formatted clearly so the LLM can ground its answer.
    """
    # TODO 1.3.a — render each hit into a human-readable line.
    # Each hit looks like {"memory": "...", "metadata": {"service_name": "...", ...}}.
    # The on-call engineer needs to see service name + description, not raw JSON.
    rendered_hits = ""

    # TODO 1.3.b — assemble the final prompt. Aim for something like:
    #
    #   ## Context retrieved from infrastructure memory
    #   - kafka-broker (data, tier 1): event backbone for async messaging…
    #   - postgres-primary (data, tier 1): source of truth for transactional data…
    #
    #   ## Question
    #   {query}
    #
    #   Answer concretely. Name services. Cite the cascade path.
    #
    # Test 1.3 will fail if the assembled prompt does not contain the query
    # AND at least one hit's `memory` text.
    prompt = SYSTEM_PROMPT + "\n\n" + query
    return prompt
