"""Tests for the FlightData data-access layer."""

from datetime import date

import query_list as ql


def test_find_flight_by_id_returns_one_row(flight_data):
    """A known ID returns exactly one record."""
    rows = flight_data.find_flight_by_id(1)
    assert len(rows) == 1
    assert rows[0].ID == 1


def test_find_missing_flight_returns_empty_list(flight_data):
    """An unknown ID returns an empty list, not an error."""
    assert flight_data.find_flight_by_id(999999) == []


def test_delayed_flights_by_origin_respects_threshold(flight_data):
    """Only flights from the requested airport delayed past the threshold appear."""
    rows = flight_data.get_delayed_flights_by_origin("JFK")
    assert rows
    assert all(row.airport == "JFK" for row in rows)
    assert all(row.delay > ql.DELAY for row in rows)


def test_origin_query_is_parameterised(flight_data):
    """An injection-style airport code matches nothing instead of every row."""
    assert flight_data.get_delayed_flights_by_origin("JFK' OR '1'='1") == []


def test_flights_by_date_only_returns_that_day(flight_data):
    """Every row returned for a date carries that year, month and day."""
    rows = flight_data.get_flights_by_date(date(2015, 1, 5))
    assert rows
    assert {(row.YEAR, row.MONTH, row.DAY) for row in rows} == {(2015, 1, 5)}


def test_airline_totals_cover_every_airline(flight_data):
    """Each of the five synthetic airlines appears once with a flight count."""
    rows = flight_data.get_airlines_total_delays_and_flights()
    assert len(rows) == 5
    assert sum(row.total_flights for row in rows) <= 2000


def test_insert_update_delete_round_trip(flight_data):
    """A new flight can be inserted, updated, then deleted."""
    flight = {"id": 5001, "airline": 2, "delay": 45}
    flight_data.insert_flight_into_flights(flight)
    assert flight_data.find_flight_by_id(5001)[0].DEPARTURE_DELAY == 45

    flight_data.update_flight({"id": 5001, "airline": 3, "delay": 90})
    updated = flight_data.find_flight_by_id(5001)[0]
    assert (updated.AIRLINE, updated.DEPARTURE_DELAY) == (3, 90)

    flight_data.delete_flight(5001)
    assert flight_data.find_flight_by_id(5001) == []
