def test_countries_returns_distinct_sorted_list(client):
    r = client.get("/api/countries")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) > 0
    assert items == sorted(items)
    assert len(items) == len(set(items))
