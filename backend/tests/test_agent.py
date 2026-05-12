def test_agent_chat_returns_suggestions(client):
    r = client.post(
        "/api/agent/chat",
        json={"session_id": "test-session", "message": "Italy culture and food"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert "suggested_tour_ids" in body
    assert isinstance(body["suggested_tour_ids"], list)
    assert len(body["suggested_tour_ids"]) <= 3
