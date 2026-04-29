import os
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.agents.graph import compile_triage_graph
from src.infrastructure.models import Incident, Severity


def _neo4j_available() -> bool:
    if os.environ.get("SKIP_NEO4J_TESTS"):
        return False
    try:
        from src.memory.config import get_neo4j_driver
        driver = get_neo4j_driver()
        try:
            with driver.session() as session:
                session.run("RETURN 1").consume()
        finally:
            driver.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _neo4j_available(), reason="Neo4j is not running.")
class TestEndToEndIncident:
    def test_given_graph_when_invoke_with_incident_then_completes_pipeline(self):
        incident = Incident(
            incident_id="INC-TEST01",
            service_name="kafka-broker",
            severity=Severity.HIGH,
            description="High latency on kafka-broker",
            symptoms=["latency_spike"],
        )

        mock_memory = MagicMock()
        mock_memory.search.return_value = {
            "results": [
                {
                    "id": "mem-1",
                    "memory": "Service: kafka-broker. Department: data. Tier: 1.",
                    "metadata": {"type": "service", "service_name": "kafka-broker", "department": "data"},
                    "score": 0.95,
                }
            ]
        }
        mock_memory.add.return_value = {"results": []}

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content=(
                '{"service_name": "kafka-broker", '
                '"severity_classification": "high", '
                '"department": "data", '
                '"reasoning": "Kafka broker has high latency", '
                '"context_found": "Kafka is a tier-1 data service"}'
            )
        )

        with patch("src.agents.triage.get_memory", return_value=mock_memory), \
             patch("src.agents.triage.ChatOllama", return_value=mock_llm), \
             patch("src.agents.specialists.platform.get_memory", return_value=mock_memory), \
             patch("src.agents.specialists.data.get_memory", return_value=mock_memory), \
             patch("src.agents.specialists.product.get_memory", return_value=mock_memory), \
             patch("src.agents.specialists.ml.get_memory", return_value=mock_memory), \
             patch("src.agents.specialists.infra.get_memory", return_value=mock_memory), \
             patch("src.agents.specialists.data.ChatOllama", return_value=mock_llm), \
             patch("src.agents.specialists.platform.ChatOllama", return_value=mock_llm), \
             patch("src.agents.specialists.product.ChatOllama", return_value=mock_llm), \
             patch("src.agents.specialists.ml.ChatOllama", return_value=mock_llm), \
             patch("src.agents.specialists.infra.ChatOllama", return_value=mock_llm):

            graph = compile_triage_graph()
            result = graph.invoke({
                "messages": [],
                "incident": incident,
                "service_name": "",
                "department": None,
                "department_knowledge": "",
                "blast_radius_report": None,
                "specialist_analysis": "",
                "final_report": "",
                "triage_classification": "",
                "routing_decision": "",
            })

            assert result["service_name"] == "kafka-broker"
            assert result["department"] is not None
            assert result["triage_classification"] != ""
            assert result["blast_radius_report"] is not None
            assert result["blast_radius_report"].root_service == "kafka-broker"
            assert result["specialist_analysis"] != ""
