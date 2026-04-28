"""
Exercise 3.2 — Router decision
==============================
The router currently picks a specialist by regexing the service name. That
worked when there were 4 services. Now we have 20 and several incidents
span multiple departments — the regex misses cross-department impact and
sometimes routes to the wrong team entirely.

Fix: read `blast_radius_report.affected_departments` from the agent state
and pick the specialist for the department that owns the failing service,
flagging cross-department incidents explicitly.
"""
from typing import Any

from src.infrastructure.models import BlastRadiusReport, Department


def decide_route(
    *,
    service_name: str,
    triage_department: Department,
    blast_radius_report: BlastRadiusReport | None,
) -> dict[str, Any]:
    """Return the routing decision based on agent state.

    Returns a dict with:
        target_department (Department) — which specialist runs next
        cross_department  (bool)        — does the blast cross teams?
        rationale         (str)         — human-readable why
    """
    # TODO 3.2.a — when blast_radius_report is None, fall back to the
    # triage_department. That's the only case where regex-by-name is OK.
    target = triage_department

    # TODO 3.2.b — when a blast report IS present, the target should be
    # the department of the FAILING service (which is `triage_department`),
    # but flag cross_department=True if more than one department appears in
    # blast_radius_report.affected_departments.
    cross = False

    # TODO 3.2.c — write a one-line rationale.
    rationale = ""

    return {
        "target_department": target,
        "cross_department": cross,
        "rationale": rationale,
    }
