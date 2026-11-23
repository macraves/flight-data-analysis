"""Tests for the Flask API endpoints."""


def test_get_flight_by_id(client):
    """GET /api/flight/<id> returns the flight as a JSON list."""
    response = client.get("/api/flight/1")
    assert response.status_code == 200
    assert response.get_json()[0]["ID"] == 1


def test_get_missing_flight_says_not_found(client):
    """An unknown ID returns a plain-text message."""
    response = client.get("/api/flight/999999")
    assert "No flight found" in response.get_data(as_text=True)


def test_add_flight_then_read_it_back(client):
    """POST /api/flights stores a flight that GET can then return."""
    payload = {"id": 5001, "airline": 2, "delay": 45}
    response = client.post("/api/flights", json=payload)
    assert "added successfully" in response.get_data(as_text=True)
    assert client.get("/api/flight/5001").get_json()[0]["ID"] == 5001


def test_add_duplicate_flight_is_rejected(client):
    """POST with an existing ID returns HTTP 400."""
    response = client.post("/api/flights", json={"id": 1, "airline": 1, "delay": 5})
    assert response.status_code == 400


def test_update_cannot_change_the_id(client):
    """PUT with a different ID in the body returns HTTP 400."""
    response = client.put("/api/flights/1", json={"id": 2, "airline": 1, "delay": 5})
    assert response.status_code == 400


def test_update_changes_the_flight(client):
    """PUT with matching IDs updates the stored delay."""
    response = client.put("/api/flights/1", json={"id": 1, "airline": 1, "delay": 77})
    assert "updated successfully" in response.get_data(as_text=True)
    assert client.get("/api/flight/1").get_json()[0]["ID"] == 1


def test_delete_flight_then_it_is_gone(client):
    """DELETE removes the flight, and a second DELETE returns HTTP 404."""
    assert "deleted successfully" in client.delete("/api/flights/1").get_data(as_text=True)
    assert "No flight found" in client.get("/api/flight/1").get_data(as_text=True)
    assert client.delete("/api/flights/1").status_code == 404


def test_flights_by_date(client):
    """GET /api/flights with a date returns that day's flights."""
    response = client.get("/api/flights?year=2015&month=1&day=5")
    flights = response.get_json()
    assert flights
    assert all(flight["DAY"] == 5 for flight in flights)


def test_bad_date_reports_format_error(client):
    """A malformed date produces the format error message."""
    response = client.get("/api/flights?year=2015&month=13&day=40")
    assert "Invalid date format" in response.get_data(as_text=True)
