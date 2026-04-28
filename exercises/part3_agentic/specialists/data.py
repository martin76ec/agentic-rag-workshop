"""
Exercise 3.4 — Specialist prompt
================================
Every specialist currently uses the same generic system prompt:

    "You are an infrastructure specialist. Provide a root cause and
    mitigation for the given incident."

That's why the agentic mode's response sounds the same as plain RAG. The
"agentic" win comes from per-department EXPERT prompts that mention the
specific tools, runbooks, and tribal knowledge of that team.

Fix: write a specialist prompt for the DATA team that names the actual
services they own and the actual commands they would run.
"""

# TODO 3.4.a — write a system prompt that:
#   - Names the services this specialist owns:
#       postgres-primary, redis-cache, kafka-broker, clickhouse-analytics
#   - Lists their concrete operational expertise (replication, partitions,
#     consumer lag, eviction policies).
#   - Asks for a structured response with: root cause hypothesis, immediate
#     mitigation, long-term remediation, impact assessment.
#
# A test will fail if the prompt does not mention all four service names
# AND at least 3 of the operational concepts (replication, failover,
# partition, lag, eviction, schema, query, consumer).

DATA_SYSTEM_PROMPT = (
    "You are an infrastructure specialist. Provide a root cause and "
    "mitigation for the given incident."
)


def build_specialist_prompt(triage_summary: str, blast_summary: str, vector_context: str) -> str:
    """Assemble the user message for the data specialist."""
    # TODO 3.4.b — compose a prompt that gives the specialist:
    #   - The triage summary (what triage classified)
    #   - The blast summary (what's downstream)
    #   - The vector context (relevant docs)
    #   - A clear ask: root cause, mitigation, remediation, impact.
    return triage_summary
