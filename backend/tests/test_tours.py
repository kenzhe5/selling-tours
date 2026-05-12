import pytest


def test_list_tours_returns_paginated_envelope(client):
    r = client.get("/api/tours")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"items", "total", "page", "size"}
    assert body["page"] == 1
    assert body["size"] == 20
    assert body["total"] > 0
    assert len(body["items"]) == min(body["total"], 20)


def test_filter_by_country(client):
    r = client.get("/api/tours", params={"country": "Italy"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    for item in body["items"]:
        assert item["country"] == "Italy"


def test_filter_by_price_range(client):
    r = client.get("/api/tours", params={"price_min": 1000, "price_max": 1500})
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert 1000 <= item["price"] <= 1500


def test_sort_price_asc(client):
    r = client.get("/api/tours", params={"sort": "price_asc", "size": 100})
    assert r.status_code == 200
    prices = [it["price"] for it in r.json()["items"]]
    assert prices == sorted(prices)


def test_pagination_size_limits(client):
    r = client.get("/api/tours", params={"size": 3, "page": 1})
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 3
    assert body["size"] == 3


def test_invalid_sort_value_returns_422(client):
    r = client.get("/api/tours", params={"sort": "not_a_sort"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_get_tour_by_id_happy_path(client):
    listing = client.get("/api/tours").json()
    tour_id = listing["items"][0]["id"]
    r = client.get(f"/api/tours/{tour_id}")
    assert r.status_code == 200
    assert r.json()["id"] == tour_id


def test_get_tour_by_id_not_found(client):
    r = client.get("/api/tours/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "tour_not_found"


def test_get_tour_by_id_invalid_uuid(client):
    r = client.get("/api/tours/not-a-uuid")
    assert r.status_code == 422
