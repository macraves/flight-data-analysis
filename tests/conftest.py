"""Shared fixtures: a synthetic database, a data-access object, and an API client."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import make_sample_db  # noqa: E402
from data import FlightData  # noqa: E402


@pytest.fixture
def database_uri(tmp_path):
    """Build a fresh synthetic database and return its SQLAlchemy URI.

    Args:
        tmp_path: pytest temporary directory, unique per test.

    Returns:
        A ``sqlite:///`` URI pointing at the new database file.
    """
    path = make_sample_db.build(tmp_path / "flights.sqlite3")
    return f"sqlite:///{path.as_posix()}"


@pytest.fixture
def flight_data(database_uri):
    """Open the data-access layer on the synthetic database.

    Args:
        database_uri: URI from the ``database_uri`` fixture.

    Returns:
        A ready ``FlightData`` object.
    """
    return FlightData(database_uri)


@pytest.fixture
def client(flight_data, monkeypatch):
    """Return a Flask test client wired to the synthetic database.

    Args:
        flight_data: Data-access object on the synthetic database.
        monkeypatch: pytest fixture used to swap the module-level object.

    Returns:
        A Flask test client for ``flight_data_app``.
    """
    import flight_data_app

    monkeypatch.setattr(flight_data_app, "FLIGHT_DATA", flight_data)
    return flight_data_app.app.test_client()
