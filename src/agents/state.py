from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from src.infrastructure.models import BlastRadiusReport, Department, Incident


class TriageState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    incident: Incident | None
    service_name: str
    department: Department | None
    department_knowledge: str
    blast_radius_report: BlastRadiusReport | None
    specialist_analysis: str
    final_report: str
    triage_classification: str
    routing_decision: str
