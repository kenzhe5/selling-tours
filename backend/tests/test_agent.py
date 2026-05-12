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


def test_agent_chat_stream_finished_with_done_event(client):
    with client.stream(
        "POST",
        "/api/agent/chat/stream",
        json={"session_id": "test-session", "message": "Italy culture and food"},
    ) as r:
        assert r.status_code == 200
        chunks: list[str] = []
        for chunk in r.iter_raw():
            if isinstance(chunk, (bytes, bytearray)):
                chunks.append(chunk.decode("utf-8"))
            else:
                chunks.append(str(chunk))
        buffer = "".join(chunks)
    assert '"event"' in buffer
    assert '"done"' in buffer
    assert '"reply"' in buffer and '"suggested_tour_ids"' in buffer
