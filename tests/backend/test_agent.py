"""Tests for the LangGraph agent pipeline — Supervisor/Worker pattern."""
from unittest.mock import MagicMock, patch


def test_safe_llm_call_success():
    from src.backend.agent import _safe_llm_call
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="test response")
    assert _safe_llm_call(mock_llm, "prompt") == "test response"


def test_safe_llm_call_error():
    from src.backend.agent import _safe_llm_call
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("Bedrock timeout")
    assert "[Error:" in _safe_llm_call(mock_llm, "prompt")


def test_safe_llm_call_fallback():
    from src.backend.agent import _safe_llm_call
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = Exception("fail")
    assert _safe_llm_call(mock_llm, "prompt", fallback="default") == "default"


def test_rewrite_query_no_history():
    from src.backend.agent import rewrite_query_node
    result = rewrite_query_node({"query": "design a lipid", "chat_history": ""})
    assert result["rewritten_query"] == "design a lipid"


def test_router_synthesis(mock_bedrock):
    from src.backend.agent import router_node
    mock_bedrock["llm_fast"].invoke.return_value = MagicMock(content="synthesis")
    result = router_node({"query": "Design a 3-tail lipid", "rewritten_query": "Design a 3-tail lipid"})
    assert result["query_type"] == "synthesis"


def test_router_lookup(mock_bedrock):
    from src.backend.agent import router_node
    mock_bedrock["llm_fast"].invoke.return_value = MagicMock(content="lookup")
    result = router_node({"query": "What is MW of DLin-MC3?", "rewritten_query": "What is MW of DLin-MC3?"})
    assert result["query_type"] == "lookup"


def test_router_general(mock_bedrock):
    from src.backend.agent import router_node
    mock_bedrock["llm_fast"].invoke.return_value = MagicMock(content="general")
    result = router_node({"query": "Latest LNP methods", "rewritten_query": "Latest LNP methods"})
    assert result["query_type"] == "general"


def test_router_fallback(mock_bedrock):
    from src.backend.agent import router_node
    mock_bedrock["llm_fast"].invoke.return_value = MagicMock(content="garbage")
    assert router_node({"query": "test", "rewritten_query": "test"})["query_type"] == "synthesis"


# --- Conditional routing ---

def test_route_synthesis():
    from src.backend.agent import route_after_retrieval
    result = route_after_retrieval({"query_type": "synthesis"})
    assert "reaction_expert" in result
    assert "design_rules" in result
    assert "synthesis_planner" in result
    assert "literature_search" in result
    assert "web_search" not in result


def test_route_lookup():
    from src.backend.agent import route_after_retrieval
    result = route_after_retrieval({"query_type": "lookup"})
    assert result == ["literature_search"]


def test_route_general():
    from src.backend.agent import route_after_retrieval
    result = route_after_retrieval({"query_type": "general"})
    assert "web_search" in result
    assert "literature_search" in result
    assert "reaction_expert" not in result


# --- Expert workers ---

def test_synthesis_planner_is_parallel_expert(mock_bedrock):
    """Synthesis planner now runs in parallel with other experts, not sequentially."""
    from src.backend.agent import synthesis_planner_node
    result = synthesis_planner_node({"query": "test", "retrieved_context": "ctx"})
    assert "synthesis_plan" in result
    mock_bedrock["llm_fast"].invoke.assert_called_once()  # uses fast model like other experts


def test_reaction_expert(mock_bedrock):
    from src.backend.agent import reaction_expert_node
    result = reaction_expert_node({"query": "test", "retrieved_context": "ctx"})
    assert "reaction_analysis" in result


def test_design_rules(mock_bedrock):
    from src.backend.agent import design_rules_node
    result = design_rules_node({"query": "test", "retrieved_context": "ctx"})
    assert "design_rules_check" in result


# --- Lead Agent ---

def test_lead_agent_synthesis(mock_bedrock):
    from src.backend.agent import lead_agent_node
    state = {
        "query": "Design a lipid", "query_type": "synthesis", "chat_history": "",
        "retrieved_context": "ctx", "reaction_analysis": "rxn", "design_rules_check": "rules",
        "synthesis_plan": "plan", "literature_context": "lit", "web_context": "",
    }
    result = lead_agent_node(state)
    assert "final_answer" in result
    # Verify the prompt includes all expert outputs
    prompt = mock_bedrock["llm"].invoke.call_args[0][0]
    assert "Reaction Expert" in prompt
    assert "Design Rules" in prompt
    assert "Synthesis Planner" in prompt
    assert "Literature" in prompt


def test_lead_agent_lookup_minimal(mock_bedrock):
    """For lookup queries, lead agent should work with just literature."""
    from src.backend.agent import lead_agent_node
    state = {
        "query": "What is DLin-MC3?", "query_type": "lookup", "chat_history": "",
        "retrieved_context": "ctx", "reaction_analysis": "", "design_rules_check": "",
        "synthesis_plan": "", "literature_context": "lit results", "web_context": "",
    }
    result = lead_agent_node(state)
    assert "final_answer" in result
    prompt = mock_bedrock["llm"].invoke.call_args[0][0]
    assert "factual lookup" in prompt.lower()
    assert "Reaction Expert" not in prompt  # empty fields not included


def test_lead_agent_includes_history(mock_bedrock):
    from src.backend.agent import lead_agent_node
    state = {
        "query": "what about 3 tails?", "query_type": "synthesis",
        "chat_history": "User: design a lipid\nAssistant: Here is one...",
        "retrieved_context": "c", "reaction_analysis": "r", "design_rules_check": "d",
        "synthesis_plan": "s", "literature_context": "", "web_context": "",
    }
    lead_agent_node(state)
    prompt = mock_bedrock["llm"].invoke.call_args[0][0]
    assert "design a lipid" in prompt


# --- Graph structure ---

def test_graph_structure():
    from src.backend.agent import graph
    nodes = set(graph.nodes.keys())
    expected = {"rewrite_query", "router", "retrieve", "reaction_expert", "design_rules",
                "synthesis_planner", "literature_search", "web_search", "lead_agent", "__start__"}
    assert expected.issubset(nodes)
    # Verify old nodes are gone
    assert "final_answer" not in nodes


# --- Full pipeline ---

def test_run_agent(mock_bedrock, mock_retriever):
    from src.backend.agent import run_agent
    mock_bedrock["llm_fast"].invoke.return_value = MagicMock(content="synthesis")
    mock_bedrock["llm"].invoke.return_value = MagicMock(content="Lead agent response")
    with patch("src.backend.agent.search_pubmed", return_value="- Paper"), \
         patch("src.backend.agent.search_pubchem", return_value="- Compound"), \
         patch("src.backend.agent.search_web", return_value="- Web"):
        result = run_agent("design a lipid", chat_history="")
    assert result["final_answer"] == "Lead agent response"
    assert result["reaction_analysis"]  # experts ran
    assert result["synthesis_plan"]     # synthesis planner ran as expert
