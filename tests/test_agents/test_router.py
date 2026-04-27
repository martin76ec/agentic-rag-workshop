from src.agents.router import router_node
from src.agents.state import TriageState
from src.infrastructure.models import BlastRadiusReport, Department, Severity


class TestRouterNode:
    def test_given_platform_department_when_route_then_routes_to_platform(self):
        state: TriageState = {
            "messages": [],
            "incident": None,
            "service_name": "api-gateway",
            "department": Department.PLATFORM,
            "department_knowledge": "",
            "blast_radius_report": None,
            "specialist_analysis": "",
            "final_report": "",
            "triage_classification": "test",
            "routing_decision": "",
        }
        result = router_node(state)
        assert result["department"] == Department.PLATFORM
        assert "platform" in result["routing_decision"]

    def test_given_unknown_department_when_route_then_routes_by_service_name(self):
        state: TriageState = {
            "messages": [],
            "incident": None,
            "service_name": "postgres-primary",
            "department": None,
            "department_knowledge": "",
            "blast_radius_report": None,
            "specialist_analysis": "",
            "final_report": "",
            "triage_classification": "test",
            "routing_decision": "",
        }
        result = router_node(state)
        assert result["department"] == Department.DATA

    def test_given_cross_department_blast_when_route_then_flags_cross_department(self):
        blast = BlastRadiusReport(
            incident_id="INC-001",
            root_service="kafka-broker",
            affected_services=["order-service", "notification-service"],
            affected_departments=[Department.DATA, Department.PRODUCT],
            propagation_paths=[["kafka-broker", "order-service"]],
            estimated_impact=Severity.HIGH,
        )
        state: TriageState = {
            "messages": [],
            "incident": None,
            "service_name": "kafka-broker",
            "department": Department.DATA,
            "department_knowledge": "",
            "blast_radius_report": blast,
            "specialist_analysis": "",
            "final_report": "",
            "triage_classification": "test",
            "routing_decision": "",
        }
        result = router_node(state)
        assert "CROSS-DEPARTMENT" in result["routing_decision"]
