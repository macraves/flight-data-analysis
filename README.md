# Flight Delay Analysis

A Python command-line tool and Flask REST API for exploring flight delays stored in a SQLite database. It runs SQL queries through SQLAlchemy, draws delay charts with matplotlib and seaborn, and builds a route map with folium.

The code started as a course assignment. The original database is not published here, so `make_sample_db.py` generates a **synthetic** stand-in with the same table layout. Delay figures from that stand-in are random and mean nothing; it exists so the project can run and be tested.

## What it does

**Command-line menu** (`src/main.py`). The menu is built from the functions in `flight_data.py`, so adding a function adds a menu entry. Current options:

| Group | Function | Output |
| --- | --- | --- |
| Charts | Delayed flights from one airport | Bar chart |
| | Delays by airport and airline | Scatter plot |
| | Delays per airline | Bar chart |
| | Delays per hour of day | Bar chart |
| Route views | Origin-destination delay scatter | matplotlib scatter |
| | Origin-destination delay heatmap (the function is named "by airline", but it groups by route) | seaborn heatmap |
| | Route map for one origin airport | folium map saved as `<CODE> overview.html` |
| Lookups | Flight by ID, flights by date, delayed flights by airline or airport | Printed table |

A flight counts as delayed when it leaves more than 20 minutes late (`DELAY` in `src/query_list.py`).

**REST API** (`src/flight_data_app.py`):

| Method | Endpoint | What it does |
| --- | --- | --- |
| GET | `/api/flight/<id>` | One flight by ID |
| GET | `/api/flights?year=&month=&day=` | Flights on a date |
| GET | `/api/airline/delays/date?year=&month=&day=` | Delayed flights on a date, with airline names |
| POST | `/api/flights` | Add a flight (`id`, `airline`, `delay`) |
| PUT | `/api/flights/<id>` | Update a flight; the ID cannot change |
| DELETE | `/api/flights/<id>` | Delete a flight |

## Design

- `data.py` is a data-access layer: one `FlightData` class owns the SQLAlchemy engine, and every method passes values to SQL as bound parameters (`:origin`, `:id`). Raw user input is never joined into a query string. `tests/test_data.py` checks that an injection-style airport code matches nothing.
- `query_list.py` holds every SQL statement in one place, away from the Python that runs it.
- Failed writes raise a `CrudError`, which the API turns into an error response.
- `main_plot.py` holds all chart and map code, separate from the query logic.

## Expected database layout

The queries expect three tables. `make_sample_db.py` creates all of them.

| Table | Columns the code uses |
| --- | --- |
| `flights` | `ID`, `YEAR`, `MONTH`, `DAY`, `FLIGHT_NUMBER`, `TAIL_NUMBER`, `AIRLINE` (an `airlines.ID`), `ORIGIN_AIRPORT`, `DESTINATION_AIRPORT`, `SCHEDULED_DEPARTURE` (`HH:MM` text), `SCHEDULED_ARRIVAL`, `DEPARTURE_DELAY`, `ARRIVAL_DELAY` (minutes) |
| `airlines` | `ID`, `AIRLINE` |
| `airports` | `IATA_CODE`, `LATITUDE`, `LONGITUDE` |

## Run it

Tested with Python 3.14.

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python make_sample_db.py       # writes src/data/flights.sqlite3
cd src
python main.py                 # command-line menu
python flight_data_app.py      # API on http://127.0.0.1:5000
cd ..
python -m pytest               # 16 tests
```

Run the programs from inside `src/`. The database path is relative to the working directory. To use your own data, put a SQLite file with the layout above at `src/data/flights.sqlite3`.

## Known issues

These are real behaviours I found while documenting the project. They are listed here instead of hidden.

1. **The "percentage of delayed flights" charts are not percentages of flights.** The airline, per-hour and route-heatmap charts compute `(total delay hours ÷ number of flights) × 100`. That measures delay hours per flight, so it can exceed 100 and does not match the axis label.
2. **API status codes are wrong on success and on some errors.** The code writes `jsonify({...}, 201)` where it needs `jsonify({...}), 201`. The HTTP status stays 200 and the response body becomes `[{...}, 201]`. A successful POST returns `[{"message": "Flight added successfully"}, 201]` with status 200. A malformed date returns status 200 with a 400 inside the body. The duplicate-ID and missing-flight paths use the correct form.
3. **A partial PUT body returns HTTP 500.** The validation uses `not any(key in flight ...)` where it needs `all`, so a body missing `delay` raises `KeyError`.
4. **The per-hour chart assumes `SCHEDULED_DEPARTURE` is `HH:MM` text.** It reads the first two characters as the hour. An integer `HHMM` column would break it.
5. **The API runs with `debug=True`.** Fine on a laptop, not safe to expose.
6. **`query_list.py` special-cases a folder name from the original course workspace** to pick the database path. It is harmless elsewhere, but is leftover scaffolding.
7. **The route-map option prompts for an airport code**, so it cannot be tested without simulated input. It has no automated test.

## Changes from the original code

The git history keeps the original files and each change separate:

1. `Import flight delay analysis code` copies the code unchanged from my `flask-wtform` repository.
2. `Replace removed matplotlib cm.get_cmap` fixes the scatter heat map, which crashed on matplotlib 3.9 and later.
3. `Add synthetic sample database, tests and pinned requirements` makes the project runnable and tested. It also adds `requests` to the requirements, which `ioput.py` imports.
