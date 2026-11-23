"""Build a small synthetic flights database for running and testing the project.

The original course database is not published, so this script generates a
stand-in with the same three tables the queries expect: ``flights``,
``airlines`` and ``airports``. All rows are random and seeded; none of it is
real flight data, so delay statistics from it mean nothing.

Usage:
    python make_sample_db.py            # writes src/data/flights.sqlite3
    python make_sample_db.py out.sqlite3
"""

from __future__ import annotations

import random
import sqlite3
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "src" / "data" / "flights.sqlite3"

AIRLINES = [
    (1, "Alpha Air"),
    (2, "Bravo Airways"),
    (3, "Charlie Jet"),
    (4, "Delta Wings"),
    (5, "Echo Express"),
]

# IATA code, name, city, state, country, latitude, longitude
AIRPORTS = [
    ("JFK", "John F. Kennedy International", "New York", "NY", "USA", 40.6398, -73.7789),
    ("LAX", "Los Angeles International", "Los Angeles", "CA", "USA", 33.9425, -118.4081),
    ("ORD", "Chicago O'Hare International", "Chicago", "IL", "USA", 41.9786, -87.9048),
    ("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta", "GA", "USA", 33.6367, -84.4281),
    ("DFW", "Dallas/Fort Worth International", "Dallas", "TX", "USA", 32.8969, -97.0381),
    ("DEN", "Denver International", "Denver", "CO", "USA", 39.8617, -104.6732),
    ("SEA", "Seattle-Tacoma International", "Seattle", "WA", "USA", 47.4502, -122.3088),
    ("SFO", "San Francisco International", "San Francisco", "CA", "USA", 37.6189, -122.3750),
]

SCHEMA = """
CREATE TABLE airlines (ID INTEGER PRIMARY KEY, AIRLINE TEXT);
CREATE TABLE airports (
    IATA_CODE TEXT PRIMARY KEY, AIRPORT TEXT, CITY TEXT, STATE TEXT,
    COUNTRY TEXT, LATITUDE REAL, LONGITUDE REAL
);
CREATE TABLE flights (
    ID INTEGER PRIMARY KEY, YEAR INTEGER, MONTH INTEGER, DAY INTEGER,
    FLIGHT_NUMBER INTEGER, TAIL_NUMBER TEXT, AIRLINE INTEGER,
    ORIGIN_AIRPORT TEXT, DESTINATION_AIRPORT TEXT,
    SCHEDULED_DEPARTURE TEXT, SCHEDULED_ARRIVAL TEXT,
    DEPARTURE_DELAY REAL, ARRIVAL_DELAY REAL
);
"""


def _delay(rng: random.Random) -> float | None:
    """Draw one departure or arrival delay in minutes.

    Args:
        rng: Seeded random generator.

    Returns:
        ``None`` for a cancelled flight (about 2%), a large delay for about
        20% of flights, and a small early or on-time value otherwise.
    """
    roll = rng.random()
    if roll < 0.02:
        return None
    if roll < 0.22:
        return float(rng.randint(21, 180))
    return float(rng.randint(-10, 20))


def build(path: Path | str, flights: int = 2000, seed: int = 0) -> Path:
    """Create the synthetic database, replacing any existing file.

    Args:
        path: Where to write the SQLite file. Parent folders are created.
        flights: Number of flight rows to generate.
        seed: Seed for the random generator, so output is reproducible.

    Returns:
        The path of the written database.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    rng = random.Random(seed)
    codes = [airport[0] for airport in AIRPORTS]

    rows = []
    for flight_id in range(1, flights + 1):
        origin, destination = rng.sample(codes, 2)
        hour, minute = rng.randint(5, 22), rng.choice([0, 15, 30, 45])
        arrival_hour = (hour + rng.randint(2, 6)) % 24
        rows.append(
            (
                flight_id, 2015, 1, rng.randint(1, 31), rng.randint(100, 2999),
                f"N{rng.randint(100, 999)}XX", rng.choice(AIRLINES)[0],
                origin, destination, f"{hour:02d}:{minute:02d}",
                f"{arrival_hour:02d}:{minute:02d}", _delay(rng), _delay(rng),
            )
        )

    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.executemany("INSERT INTO airlines VALUES (?, ?)", AIRLINES)
        connection.executemany("INSERT INTO airports VALUES (?, ?, ?, ?, ?, ?, ?)", AIRPORTS)
        connection.executemany(
            "INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows
        )
    connection.close()
    return path


def main() -> None:
    """Build the database at the path given on the command line, or the default."""
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    build(target)
    print(f"Wrote synthetic database to {target}")


if __name__ == "__main__":
    main()
