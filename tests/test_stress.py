"""Bounded offline stress simulations; no provider calls or genuine writes.

Run: uv run --locked python -m pytest -q -s tests/test_stress.py
Timings are observations, not machine-dependent pass/fail thresholds.
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from time import perf_counter
from uuid import uuid4

import pytest
import requests
from weather_fakes import (
    CATALOG, Clock, FakeSession, catalog_handler, make_client,
)

from weather_app.analytics import AVAILABLE
from weather_app.config import load_product_defaults
from weather_app.dashboard import overview_preferences
from weather_app.executive import executive_summary
from weather_app.searcher import search_destinations
from weather_app.service import WeatherService
from weather_app.storage import WeatherStore


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Stress simulations must remain offline")
    monkeypatch.setattr(requests.Session, "request", blocked)


def setup_service(tmp_path):
    clock = Clock(datetime(2026, 11, 13, 6, tzinfo=timezone.utc))
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "synthetic_weather.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    return service, session, store, clock


def test_fifty_full_catalog_window_changes_reuse_then_expire(tmp_path):
    service, session, store, clock = setup_service(tmp_path)
    catalog = list(CATALOG.values())
    defaults = load_product_defaults()
    initial = service.forecast_many(catalog)
    assert all(r["error"] is None for r in initial.values())
    assert len(session.calls) == 83
    before = store.path.read_bytes()
    started = perf_counter()
    for index in range(50):
        preferences = overview_preferences(clock(), defaults, index % 5 + 1)
        if index % 2:
            preferences = replace(
                preferences, scoring_mode="searcher",
                rain_preference="High", wind_preference="Fresh",
            )
        result = search_destinations(catalog, preferences, service, clock())
        assert result["cached"] == 83
        assert not result["errors"]
        assert all(r["status"] == AVAILABLE for r in result["rows"])
        assert all(0 <= r["final_score"] <= 100 for r in result["rows"])
        summary = executive_summary(result["rows"], catalog)
        assert summary["available"] == 83
        canonical = {r["city_id"]: r["final_score"] for r in result["rows"]}
        assert all(r["final_score"] == canonical[r["city_id"]]
                   for rows in summary["bands"].values() for r in rows)
    elapsed = perf_counter() - started
    assert len(session.calls) == 83
    assert store.path.read_bytes() == before
    restarted = WeatherService(
        make_client(session, clock), WeatherStore(store.path), clock=clock,
    )
    assert all(r["from_cache"]
               for r in restarted.forecast_many(catalog).values())
    assert len(session.calls) == 83
    clock.advance(hours=3, seconds=1)
    expired = restarted.forecast_many(catalog)
    assert all(r["error"] is None and not r["from_cache"]
               for r in expired.values())
    assert len(session.calls) == 166
    assert len(store.load()) == 6640
    print(f"50 full-catalog changes: {elapsed:.3f}s; "
          "83 initial / 0 repeat / 83 expired fake requests")


def test_eight_parallel_writers_preserve_unique_and_duplicate_batches(
    tmp_path,
):
    service, _, store, _ = setup_service(tmp_path)
    records = service.forecast(next(iter(CATALOG.values())))["records"]
    batches = [[replace(r, fetch_id=str(uuid4())) for r in records]
               for _ in range(24)]
    # Each batch has one response ID, as the real service does.
    batches = [[replace(r, fetch_id=batch[0].fetch_id) for r in batch]
               for batch in batches]
    started = perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        written = list(pool.map(
            lambda batch: WeatherStore(store.path).append(batch),
            batches + batches,
        ))
    loaded = WeatherStore(store.path).load()
    assert sum(written) == 960
    assert len(loaded) == 1000
    assert len({r.key for r in loaded}) == 1000
    assert not list(tmp_path.glob("*.tmp"))
    print(f"8 writers / 48 save attempts: {perf_counter() - started:.3f}s; "
          "960 unique new rows, no duplicate rows")


def test_large_history_load_and_latest_lookup(tmp_path):
    service, _, store, clock = setup_service(tmp_path)
    fetched = service.forecast_many(list(CATALOG.values()))
    latest = [r for result in fetched.values() for r in result["records"]]
    historical = []
    for day in range(1, 10):
        for result in fetched.values():
            fetch_id = str(uuid4())
            historical.extend(
                replace(r, fetch_id=fetch_id,
                        retrieved_at_utc=(
                            r.retrieved_at_utc - timedelta(days=day)),
                        valid_at_utc=r.valid_at_utc - timedelta(days=day))
                for r in result["records"]
            )
    store.append(historical)
    assert len(store.load()) == 33200
    cold = WeatherStore(store.path)
    started = perf_counter()
    assert len(cold.load()) == 33200
    load_seconds = perf_counter() - started
    before = store.path.read_bytes()
    started = perf_counter()
    for place in CATALOG.values():
        records = cold.latest_forecast(place.city_id)
        assert len(records) == 40
        assert all(r.retrieved_at_utc == clock() for r in records)
    assert len(latest) == 3320
    assert store.path.read_bytes() == before
    print(f"33,200 rows: cold load {load_seconds:.3f}s; "
          f"83 cached lookups {perf_counter() - started:.3f}s")
