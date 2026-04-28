"""
Tests for Exercise 3 — Agentic RAG.

Run with:  uv run pytest exercises/part3_agentic/tests.py -v
"""

from exercises.part3_agentic import router as router_ex
from exercises.part3_agentic import state as state_ex
from exercises.part3_agentic import triage as triage_ex
from exercises.part3_agentic.specialists import data as data_ex
from src.infrastructure.models import BlastRadiusReport, Department, Severity

# ── 3.1  triage classifier ──────────────────────────────────────────────────

class TestTriage:
    def test_parses_clean_json(self):
        out = triage_ex.parse_classification(
            '{"service_name": "kafka-broker", "severity_classification": "high",'
            ' "department": "data", "reasoning": "kafka is down"}'
        )
        assert out["service_name"] == "kafka-broker"
        assert out["severity"] == Severity.HIGH
        assert out["department"] == Department.DATA

    def test_strips_markdown_fences(self):
        out = triage_ex.parse_classification(
            "```json\n"
            '{"service_name": "postgres-primary", "severity_classification": "critical",'
            ' "department": "data", "reasoning": "db down"}\n'
            "```"
        )
        assert out["service_name"] == "postgres-primary"
        assert out["severity"] == Severity.CRITICAL
        assert out["department"] == Department.DATA

    def test_extracts_json_after_prose(self):
        out = triage_ex.parse_classification(
            "Here's my analysis:\n\n"
            '{"service_name": "api-gateway", "severity_classification": "medium",'
            ' "department": "platform", "reasoning": "..."}'
        )
        assert out["department"] == Department.PLATFORM

    def test_invalid_severity_falls_back_to_medium(self):
        out = triage_ex.parse_classification(
            '{"service_name": "x", "severity_classification": "bananas",'
            ' "department": "data", "reasoning": ""}'
        )
        assert out["severity"] == Severity.MEDIUM

    def test_does_not_default_to_platform_when_data_was_correct(self):
        out = triage_ex.parse_classification(
            '{"service_name": "kafka", "severity_classification": "high",'
            ' "department": "data", "reasoning": ""}'
        )
        assert out["department"] == Department.DATA, (
            "When the LLM provides a valid department, do NOT overwrite with PLATFORM."
        )


# ── 3.2  router ────────────────────────────────────────────────────────────

class TestRouter:
    def _report(self, departments: list[Department]) -> BlastRadiusReport:
        return BlastRadiusReport(
            incident_id="X",
            root_service="kafka-broker",
            affected_services=["clickhouse-analytics"],
            affected_departments=departments,
            propagation_paths=[["kafka-broker", "clickhouse-analytics"]],
            estimated_impact=Severity.HIGH,
        )

    def test_falls_back_to_triage_dept_without_report(self):
        out = router_ex.decide_route(
            service_name="kafka-broker",
            triage_department=Department.DATA,
            blast_radius_report=None,
        )
        assert out["target_department"] == Department.DATA
        assert out["cross_department"] is False

    def test_uses_triage_department_when_report_present(self):
        out = router_ex.decide_route(
            service_name="kafka-broker",
            triage_department=Department.DATA,
            blast_radius_report=self._report([Department.DATA]),
        )
        assert out["target_department"] == Department.DATA

    def test_flags_cross_department(self):
        out = router_ex.decide_route(
            service_name="kafka-broker",
            triage_department=Department.DATA,
            blast_radius_report=self._report([Department.DATA, Department.PRODUCT, Department.ML]),
        )
        assert out["cross_department"] is True

    def test_rationale_is_not_empty(self):
        out = router_ex.decide_route(
            service_name="kafka-broker",
            triage_department=Department.DATA,
            blast_radius_report=self._report([Department.DATA]),
        )
        assert isinstance(out["rationale"], str) and out["rationale"].strip()


# ── 3.3  state ─────────────────────────────────────────────────────────────

class TestState:
    def test_state_has_required_fields(self):
        annotations = state_ex.TriageState.__annotations__
        for field in (
            "incident",
            "service_name",
            "department",
            "blast_radius_report",
            "triage_classification",
            "routing_decision",
            "specialist_analysis",
            "final_report",
        ):
            assert field in annotations, f"TriageState is missing required field: {field}"


# ── 3.4  specialist prompt ──────────────────────────────────────────────────

class TestDataSpecialist:
    def test_system_prompt_names_owned_services(self):
        prompt = data_ex.DATA_SYSTEM_PROMPT.lower()
        for svc in ("postgres-primary", "redis-cache", "kafka-broker", "clickhouse-analytics"):
            assert svc in prompt, f"Specialist prompt must mention {svc}"

    def test_system_prompt_mentions_operational_concepts(self):
        prompt = data_ex.DATA_SYSTEM_PROMPT.lower()
        concepts = ["replication", "failover", "partition", "lag", "eviction", "schema", "query", "consumer"]
        hits = sum(1 for c in concepts if c in prompt)
        assert hits >= 3, (
            f"Specialist prompt should mention at least 3 ops concepts; found {hits}."
        )

    def test_user_prompt_includes_inputs(self):
        out = data_ex.build_specialist_prompt(
            triage_summary="kafka-broker tier 1, data, high severity",
            blast_summary="affected: clickhouse-analytics, experiment-tracker",
            vector_context="kafka-broker is the event backbone",
        )
        assert "kafka-broker tier 1" in out
        assert "clickhouse-analytics" in out
        assert "event backbone" in out
