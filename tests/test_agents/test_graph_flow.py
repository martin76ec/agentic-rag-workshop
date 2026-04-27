from src.agents.graph import build_triage_graph, compile_triage_graph


class TestTriageGraph:
    def test_given_graph_when_build_then_has_three_nodes(self):
        graph = build_triage_graph()
        assert "triage" in graph.nodes
        assert "router" in graph.nodes
        assert "specialist" in graph.nodes

    def test_given_graph_when_compile_then_returns_compiled(self):
        compiled = compile_triage_graph()
        assert compiled is not None
        assert hasattr(compiled, "invoke")
        assert hasattr(compiled, "stream")
