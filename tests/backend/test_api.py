"""Tests for FastAPI endpoints."""
import json


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "region" in data


def test_reactions_list(client):
    r = client.get("/api/reactions")
    assert r.status_code == 200
    reactions = r.json()["reactions"]
    assert len(reactions) == 13
    assert all("id" in rx and "name" in rx and "smarts_reactants" in rx for rx in reactions)


def test_reaction_svg(client):
    r = client.get("/api/reactions/10001/svg")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/svg+xml"
    assert "<svg" in r.text


def test_reaction_svg_not_found(client):
    r = client.get("/api/reactions/99999/svg")
    assert r.status_code == 404


def test_analyze_smiles_valid(client):
    r = client.post("/api/analyze-smiles", json={"smiles": "CCO"})
    assert r.status_code == 200
    data = r.json()
    assert "scores" in data
    scores = data["scores"]
    assert "qed" in scores
    assert "sa_score" in scores
    assert "logp" in scores
    assert "mol_weight" in scores
    assert "svg" in data
    assert "<svg" in data["svg"]


def test_analyze_smiles_invalid(client):
    r = client.post("/api/analyze-smiles", json={"smiles": "NOT_A_SMILES"})
    assert r.status_code == 200
    assert r.json()["error"] == "Invalid SMILES"


def test_chat_stream(client):
    """Test SSE streaming chat returns proper event sequence."""
    r = client.post("/api/chat", json={"message": "test query", "chat_history": ""})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]

    events = []
    for line in r.text.strip().split("\n"):
        if line.startswith("data: ") and line.strip() != "data: [DONE]":
            events.append(json.loads(line[6:]))

    types = [e["type"] for e in events]
    assert "status" in types
    assert "answer" in types
    assert "details" in types

    # Verify details has all three expert sections
    details = next(e for e in events if e["type"] == "details")
    assert "reaction_analysis" in details
    assert "design_rules_check" in details
    assert "synthesis_plan" in details


def test_chat_stream_with_history(client):
    """Test that chat_history is accepted."""
    r = client.post("/api/chat", json={
        "message": "what about the second tail?",
        "chat_history": "User: Design a 2-tail lipid\nAssistant: Here is a design..."
    })
    assert r.status_code == 200
    assert "data: [DONE]" in r.text


def test_query_endpoint(client):
    r = client.post("/api/query", json={"query": "test", "chat_history": ""})
    assert r.status_code == 200
    data = r.json()
    assert "final_answer" in data
    assert "reaction_analysis" in data
    assert "synthesis_plan" in data
    assert "design_rules_check" in data
