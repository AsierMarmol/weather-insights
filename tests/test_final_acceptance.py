"""P5.5 regressions: safe reuse, changing files and forecast boundaries."""

from datetime import datetime, timezone
from unittest.mock import Mock
from pathlib import Path
from streamlit.testing.v1 import AppTest

import pytest
import requests
from test_storage import forecast as make_forecast
from uuid import NAMESPACE_URL, uuid5
from weather_fakes import (
    SEGOVIA, TOLEDO, Clock, FakeResponse, FakeSession, forecast_payload,
    make_client,
)

from weather_app import searcher, storage
from weather_app.models import SearchPreferences, WeatherRecord
from weather_app.service import WeatherService
from weather_app.storage import StorageError, WeatherStore


def forecast(label, **kwargs):
    return make_forecast(str(uuid5(NAMESPACE_URL, label)), **kwargs)


@pytest.fixture(autouse=True)
def no_live_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("P5.5 tests must not make live requests")
    monkeypatch.setattr(requests.Session, "request", blocked)


def test_repeated_lookups_validate_unchanged_file_only_once(
    tmp_path, monkeypatch
):
    path = tmp_path / "weather.csv"
    saved = forecast("a") + forecast("b", city_id=SEGOVIA.city_id)
    WeatherStore(path).append(saved)
    spy = Mock(wraps=WeatherRecord.from_csv_row)
    monkeypatch.setattr(WeatherRecord, "from_csv_row", spy)
    store = WeatherStore(path)
    for _ in range(20):
        assert store.latest_forecast(TOLEDO.city_id) == saved[:3]
        assert store.latest_forecast(SEGOVIA.city_id) == saved[3:]
    assert spy.call_count == len(saved)


def test_successful_appends_do_not_reparse_history(tmp_path, monkeypatch):
    store = WeatherStore(tmp_path / "weather.csv")
    store.append(forecast("a"))
    spy = Mock(wraps=WeatherRecord.from_csv_row)
    monkeypatch.setattr(WeatherRecord, "from_csv_row", spy)
    for batch in ["b", "c", "d"]:
        store.append(forecast(batch))
        store.latest_forecast(TOLEDO.city_id)
    assert len(store.load()) == 12
    assert spy.call_count == 0


def test_cached_reads_notice_other_store_and_same_size_edits(tmp_path):
    path = tmp_path / "weather.csv"
    store = WeatherStore(path)
    store.append(forecast("a"))
    store.load().clear()  # Callers cannot mutate the cached sequence.
    assert len(store.load()) == 3
    WeatherStore(path).append(forecast("b"))
    assert len(store.load()) == 6
    original = path.read_bytes()
    changed = original.replace(b"20.0", b"21.0")
    assert changed != original and len(changed) == len(original)
    path.write_bytes(changed)
    assert all(r.temperature_c == 21.0 for r in store.load())
    path.write_bytes(b"broken\n")
    with pytest.raises(StorageError):
        store.load()
    path.write_bytes(original)
    assert len(store.load()) == 6
    path.unlink()
    assert store.load() == []
    store.append(forecast("c"))
    assert len(store.load()) == 3


def test_cached_reads_still_report_permission_errors(tmp_path, monkeypatch):
    store = WeatherStore(tmp_path / "weather.csv")
    store.append(forecast("a"))
    store.load()

    def denied(path):
        raise PermissionError("synthetic denial")

    monkeypatch.setattr(storage.Path, "read_bytes", denied)
    with pytest.raises(StorageError):
        store.load()


def test_failed_write_never_enters_validated_cache(tmp_path, monkeypatch):
    store = WeatherStore(tmp_path / "weather.csv")
    store.append(forecast("a"))
    original = store.path.read_bytes()

    def fail(*args):
        raise OSError("synthetic replace failure")

    with monkeypatch.context() as patch:
        patch.setattr(storage.os, "replace", fail)
        with pytest.raises(StorageError):
            store.append(forecast("b"))
    assert store.path.read_bytes() == original
    assert len(store.load()) == 3
    assert store.append(forecast("b")) == 3
    assert len(store.load()) == 6


def test_slot_boundary_keeps_strict_window_and_explains_retry(
    tmp_path, monkeypatch
):
    run_at = datetime(2026, 11, 12, 8, 59, 59, tzinfo=timezone.utc)
    clock = Clock(run_at)

    def handle(url, params):
        place = TOLEDO if params["lat"] == TOLEDO.latitude else SEGOVIA
        if place is SEGOVIA:
            clock.now = run_at.replace(hour=9, minute=0, second=1)
        hour = 9 if clock.now.hour == 8 else 12
        first = run_at.replace(hour=hour, minute=0, second=0)
        return FakeResponse(200, forecast_payload(place, first))

    session = FakeSession(handler=handle)
    service = WeatherService(make_client(session, clock),
                             WeatherStore(tmp_path / "weather.csv"),
                             clock=clock)
    prefs = SearchPreferences(
        days=1, temperature_min_c=16, temperature_max_c=24,
        max_precipitation_probability_pct=30, max_wind_kmh=25,
    )
    result = searcher.search_destinations(
        [TOLEDO, SEGOVIA], prefs, service, run_at
    )
    rows = {r["city_id"]: r for r in result["rows"]}
    assert rows[TOLEDO.city_id]["status"] == "available"
    assert rows[SEGOVIA.city_id]["reason"] == "missing_periods"
    assert searcher.forecast_boundary_crossed(result["rows"], run_at, 1)
    assert len(session.calls) == 2  # No futile retry of a fresh forecast.
    monkeypatch.setattr(searcher, "utc_now", clock)
    app = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "app.py"),
        default_timeout=15,
    )
    state = app.session_state
    state["search_preferences"] = prefs
    state["search_result_preferences"] = prefs
    state["search_run_at_utc"] = run_at
    state["search_analysis_rows"] = result["rows"]
    state["search_errors"] = {}
    state["search_cached_count"] = 0
    app.run()
    assert not app.exception
    assert any("slot boundary" in x.value for x in app.warning)
    state["dashboard_overview"] = {
        "rows": result["rows"], "errors": {}, "cached": 0,
        "run_at": run_at, "preferences": prefs,
    }
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception
    assert any("slot boundary" in x.value for x in app.warning)
    assert any("Mainland Spain" in x.value for x in app.subheader)

    again = searcher.search_destinations(
        [TOLEDO, SEGOVIA], prefs, service, clock.now
    )
    assert all(r["status"] == "available" for r in again["rows"])
    assert len(session.calls) == 2  # New strict window can use saved data.
    assert len(service.store.load()) == 80


def test_missing_slots_without_crossing_do_not_claim_boundary():
    run_at = datetime(2026, 11, 12, 8, tzinfo=timezone.utc)
    rows = [{"reason": "missing_periods",
             "forecast_retrieved_at_utc": run_at.isoformat()}]
    assert not searcher.forecast_boundary_crossed(rows, run_at, 1)
