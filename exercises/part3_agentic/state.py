"""
Exercise 3.3 — Agent state shape
================================
The state passed between LangGraph nodes is a TypedDict. Right now it only
carries the message history — the specialist node receives empty context
because triage's BlastRadiusReport is never written to state.

Fix: extend TriageState with the fields each downstream node needs to read.
The reference shape lives in src/agents/state.py.
"""
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# TODO 3.3.a — add these imports once you reference the types below.
# from src.infrastructure.models import BlastRadiusReport, Department, Incident


class TriageState(TypedDict, total=False):
    """State shared across triage → router → specialist nodes."""

    # Message history (already wired). The Annotated[..., add_messages] tells
    # LangGraph to APPEND new messages instead of overwriting.
    messages: Annotated[list[BaseMessage], add_messages]

    # TODO 3.3.b — add the fields the downstream nodes actually read:
    #
    #   incident: Incident | None
    #       The original incident object from mock_apis.py.
    #
    #   service_name: str
    #       The service the triage classifier identified as failing.
    #
    #   department: Department | None
    #       The department triage decided owns the service.
    #
    #   blast_radius_report: BlastRadiusReport | None
    #       The output of generate_blast_radius_report(); read by the router
    #       to detect cross-department incidents.
    #
    #   triage_classification: str
    #       Human-readable triage summary; read by the specialist for context.
    #
    #   routing_decision: str
    #       The router's rationale; surfaced in the final report.
    #
    #   specialist_analysis: str
    #       The specialist's output.
    #
    #   final_report: str
    #       The composed end-of-pipeline report.
    pass
