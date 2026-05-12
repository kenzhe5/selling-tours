def _first_tour(client) -> dict:
    return client.get("/api/tours").json()["items"][0]


def test_create_booking_happy_path(client):
    tour = _first_tour(client)
    payload = {
        "tour_id": tour["id"],
        "user_name": "Alice Tester",
        "user_email": "alice@example.com",
        "start_date": tour["start_date"],
        "num_people": 2,
    }
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["tour_id"] == tour["id"]
    assert body["user_email"] == "alice@example.com"
    assert body["status"] == "confirmed"


def test_create_booking_decrements_available_slots(client):
    tour = _first_tour(client)
    before = client.get(f"/api/tours/{tour['id']}").json()["available_slots"]
    payload = {
        "tour_id": tour["id"],
        "user_name": "Bob",
        "user_email": "bob@example.com",
        "start_date": tour["start_date"],
        "num_people": 1,
    }
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 201
    after = client.get(f"/api/tours/{tour['id']}").json()["available_slots"]
    assert after == before - 1


def test_create_booking_unknown_tour_returns_404(client):
    payload = {
        "tour_id": "00000000-0000-0000-0000-000000000000",
        "user_name": "Ghost",
        "user_email": "ghost@example.com",
        "start_date": "2026-12-01",
        "num_people": 1,
    }
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "tour_not_found"


def test_create_booking_invalid_email_returns_422(client):
    tour = _first_tour(client)
    payload = {
        "tour_id": tour["id"],
        "user_name": "Bad",
        "user_email": "not-an-email",
        "start_date": tour["start_date"],
        "num_people": 1,
    }
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_create_booking_too_many_people_returns_400(client):
    tour = _first_tour(client)
    payload = {
        "tour_id": tour["id"],
        "user_name": "Greedy",
        "user_email": "greedy@example.com",
        "start_date": tour["start_date"],
        "num_people": 20,
    }
    # If the tour happens to have >= 20 slots after earlier tests, retry on another tour.
    r = client.post("/api/bookings", json=payload)
    if r.status_code == 201:
        # try a smaller-slot tour from the listing
        for t in client.get("/api/tours").json()["items"]:
            if t["available_slots"] < 20:
                payload["tour_id"] = t["id"]
                payload["start_date"] = t["start_date"]
                r = client.post("/api/bookings", json=payload)
                break
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "no_slots"


def test_list_bookings_by_email(client):
    email = "lister@example.com"
    tour = _first_tour(client)
    client.post(
        "/api/bookings",
        json={
            "tour_id": tour["id"],
            "user_name": "Lister",
            "user_email": email,
            "start_date": tour["start_date"],
            "num_people": 1,
        },
    )
    r = client.get("/api/bookings", params={"email": email})
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 1
    assert all(b["user_email"] == email for b in body)


def test_list_bookings_missing_email_returns_422(client):
    r = client.get("/api/bookings")
    assert r.status_code == 422
