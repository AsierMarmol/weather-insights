"""P4.1 tests: synthetic HTTP/temp stores and read-only genuine UI replay."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from streamlit.testing.v1 import AppTest
from weather_fakes import (
    CATALOG,
    SEGOVIA,
    TOLEDO,
    Clock,
    FakeSession,
    catalog_handler,
    make_client,
)

from weather_app import searcher
from weather_app.client import AuthenticationError
from weather_app.config import load_product_defaults
from weather_app.models import SearchPreferences
from weather_app.service import WeatherService
from weather_app.storage import WEATHER_RECORDS_PATH, WeatherStore

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 12, 6, tzinfo=timezone.utc)
SEVILLE = CATALOG["ES-41091"]


@pytest.fixture(autouse=True)
def no_live_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Tests must never make live HTTP requests")

    monkeypatch.setattr(requests.Session, "request", blocked)
    original = WEATHER_RECORDS_PATH.read_bytes()
    yield
    assert WEATHER_RECORDS_PATH.read_bytes() == original


@pytest.fixture
def ui(monkeypatch, tmp_path):
    places = [TOLEDO, SEGOVIA, SEVILLE] + [
        d for d in CATALOG.values() if d not in [TOLEDO, SEGOVIA, SEVILLE]
    ][:3]
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    service = WeatherService(
        make_client(session, clock),
        WeatherStore(tmp_path / "weather.csv"),
        clock=clock,
    )
    factory = Mock(return_value=service)
    monkeypatch.setattr(searcher, "load_destinations", lambda: places)
    monkeypatch.setattr(searcher, "utc_now", clock)
    monkeypatch.setattr(WeatherService, "from_environment", factory)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    return app, service, session, clock, places, factory


@pytest.mark.parametrize(
    "month,low,high",
    [
        (1, 10, 18),
        (4, 18, 26),
        (7, 22, 30),
        (10, 16, 24),
    ],
)
def test_initial_preferences_by_season(month, low, high):
    prefs = searcher.initial_preferences(
        NOW.replace(month=month), load_product_defaults()
    )
    assert (prefs.temperature_min_c, prefs.temperature_max_c) == (low, high)
    assert (
        prefs.days == 3 and prefs.activities == prefs.destination_sizes == ()
    )
    assert prefs.max_precipitation_probability_pct == 30
    assert prefs.max_wind_kmh == 25


def test_initial_preferences_uses_madrid_month_and_requires_aware_time():
    moment = datetime(2026, 11, 30, 23, 30, tzinfo=timezone.utc)
    assert (
        searcher.initial_preferences(
            moment, load_product_defaults()
        ).temperature_min_c
        == 10
    )
    with pytest.raises(ValueError):
        searcher.initial_preferences(moment.replace(tzinfo=None), {})


def test_controls_do_not_fetch_and_preserve_edits_across_navigation(ui):
    app, _, session, clock, _, factory = ui
    app.run()
    assert not app.exception
    assert app.multiselect(key="_trip_activities").value == ["All"]
    assert app.multiselect(key="_trip_sizes").value == ["All"]
    assert app.select_slider(key="_trip_days").value == 3
    app.number_input(key="_trip_min").set_value(12.0).run()
    app.select_slider(key="_trip_days").set_value(5).run()
    app.sidebar.radio[0].set_value("Dashboard").run()
    clock.now = NOW.replace(month=12)
    app.sidebar.radio[0].set_value("Searcher").run()
    assert not app.exception
    assert app.number_input(key="_trip_min").value == 12.0
    assert app.select_slider(key="_trip_days").value == 5
    assert not session.calls and not factory.called
    app.button(key="reset_preferences").click().run()
    assert app.number_input(key="_trip_min").value == 10.0
    assert app.select_slider(key="_trip_days").value == 3


def test_search_top_five_matches_full_ranking_and_cache(ui):
    app, service, session, _, places, factory = ui
    app.run().button(key="run_search").click().run()
    assert not app.exception
    assert len(session.calls) == len(places) == 6
    assert len(app.metric) == 15  # Three metrics for each of five cards.
    rows = app.session_state.search_analysis_rows
    assert len(rows) == 6 and all(r["status"] == "available" for r in rows)
    table = app.dataframe[0].value
    assert table["Score / 100"].tolist() == [r["final_score"] for r in rows]
    assert [float(m.value) for m in app.metric[::3]] == [
        round(r["final_score"], 1) for r in rows[:5]
    ]
    saved = service.store.path.read_bytes()
    app.button(key="run_search").click().run()
    assert not app.exception and factory.call_count == 1
    assert len(session.calls) == 6
    assert service.store.path.read_bytes() == saved
    app.number_input(key="_trip_max").set_value(19.0).run()
    assert any("last search" in m.value for m in app.info)
    assert len(session.calls) == 6
    assert app.session_state.search_analysis_rows == rows


def test_invalid_temperature_prevents_request(ui):
    app, _, session, _, _, _ = ui
    app.run().number_input(key="_trip_min").set_value(30.0).run()
    assert not app.exception and app.error
    assert app.button(key="run_search").disabled
    assert session.calls == []


def test_empty_selection_means_all_and_mismatched_filters_fetch_nothing(ui):
    app, _, session, _, places, _ = ui
    app.run().multiselect(key="_trip_activities").set_value([]).run()
    assert app.session_state.search_preferences.activities == ()
    assert app.multiselect(key="_trip_activities").value == ["All"]
    # No artificial location or empty data file is needed for empty matches.
    prefs = SearchPreferences(
        days=3,
        temperature_min_c=16,
        temperature_max_c=24,
        max_precipitation_probability_pct=30,
        max_wind_kmh=25,
        activities=("Coast",),
        destination_sizes=("Large city",),
    )
    result = searcher.search_destinations([TOLEDO], prefs, None, NOW)
    assert result["rows"] == [] and result["eligible"] == 0
    assert not session.calls


def test_filters_are_applied_before_fetch(ui):
    app, _, session, _, places, _ = ui
    app.run().multiselect(key="_trip_sizes").set_value(
        ["Small city or town"]
    ).run()
    app.button(key="run_search").click().run()
    assert not app.exception
    eligible = [
        d for d in places if d.destination_size == "Small city or town"
    ]
    assert len(session.calls) == len(eligible)
    assert {r["city_id"] for r in app.session_state.search_analysis_rows} == {
        d.city_id for d in eligible
    }


def test_partial_failure_is_visible_and_keeps_other_results(ui):
    app, _, session, clock, _, _ = ui
    session.handler = catalog_handler(clock, failures={SEGOVIA.city_id: 404})
    app.run().button(key="run_search").click().run()
    assert not app.exception
    rows = app.session_state.search_analysis_rows
    assert sum(r["status"] == "available" for r in rows) == 5
    assert rows[-1]["city_id"] == SEGOVIA.city_id
    assert any("find this place" in w.value for w in app.warning)
    assert "find this place" in app.dataframe[0].value.iloc[-1]["Status"]


def test_missing_key_has_safe_message_no_traceback(ui):
    app, _, session, _, _, factory = ui
    factory.side_effect = AuthenticationError("never-show-private-key")
    app.run().button(key="run_search").click().run()
    assert not app.exception and not session.calls
    assert "Check your local API key" in app.error[0].value
    assert "never-show" not in app.error[0].value


def test_cached_incomplete_window_refreshes_once(ui):
    _, service, _, _, _, _ = ui
    fresh = service.forecast_many([TOLEDO])
    incomplete = {
        TOLEDO.city_id: {
            **fresh[TOLEDO.city_id],
            "from_cache": True,
            "records": fresh[TOLEDO.city_id]["records"][:5],
        }
    }
    stub = Mock()
    stub.forecast_many.side_effect = [incomplete, fresh]
    result = searcher.search_destinations(
        [TOLEDO],
        searcher.initial_preferences(NOW, load_product_defaults()),
        stub,
        NOW,
    )
    assert stub.forecast_many.call_count == 2
    assert stub.forecast_many.call_args.kwargs["force_refresh"] is True
    assert result["rows"][0]["status"] == "available"


def test_genuine_saved_sample_renders_without_live_http(ui):
    app, _, _, clock, _, factory = ui
    records = WeatherStore().load(kind="forecast")
    ids = {
        "5f188094-18a9-471c-9155-81a82d6caae3",
        "93c655ea-1a12-4b06-bb42-cda59497238c",
        "9bb6a9d5-dd22-482d-ae30-85db8ed1b51b",
    }
    saved = {}
    for record in records:
        if record.fetch_id in ids:
            saved.setdefault(
                record.city_id,
                {
                    "records": [],
                    "from_cache": True,
                    "error": None,
                },
            )["records"].append(record)
    clock.now = datetime.fromisoformat("2026-11-12T11:29:04.669987+00:00")
    # Explicitly replay the historical snapshot, not a claim of fresh weather.
    stub = Mock()
    stub.forecast_many.return_value = saved
    factory.return_value = stub
    import unittest.mock

    with unittest.mock.patch.object(
        searcher, "load_destinations", return_value=[TOLEDO, SEGOVIA, SEVILLE]
    ):
        app.run().button(key="run_search").click().run()
    assert not app.exception
    assert app.dataframe[0].value["City"].tolist() == [
        "Seville",
        "Toledo",
        "Segovia",
    ]
    assert [float(m.value) for m in app.metric[::3]] == [83.9, 50.8, 46.9]


def test_old_results_show_age_warning_without_refetch(ui):
    app, _, session, clock, _, _ = ui
    app.run().button(key="run_search").click().run()
    count = len(session.calls)
    clock.advance(hours=4)
    app.run()
    assert not app.exception
    assert any("over three hours" in w.value for w in app.warning)
    assert len(session.calls) == count


def test_no_matching_combination_displays_empty_state(ui, monkeypatch):
    app, _, session, _, _, factory = ui
    monkeypatch.setattr(
        searcher,
        "load_destinations",
        lambda: [TOLEDO, CATALOG["ES-08019"]],
    )
    app.run().multiselect(key="_trip_activities").set_value(["Coast"]).run()
    app.multiselect(key="_trip_sizes").set_value(["Small city or town"]).run()
    app.button(key="run_search").click().run()
    assert not app.exception and not session.calls and not factory.called
    assert any("No destinations match" in w.value for w in app.warning)
    assert app.session_state.search_analysis_rows == []


@pytest.mark.parametrize(
    "code",
    [
        "authentication",
        "network",
        "rate_limited",
        "provider",
        "storage",
    ],
)
def test_all_failed_search_has_safe_reasons(ui, code):
    app, _, _, _, places, factory = ui
    stub = Mock()
    stub.forecast_many.return_value = {
        d.city_id: {
            "records": [],
            "from_cache": False,
            "error": {"code": code, "message": "never-show-private-key"},
        }
        for d in places
    }
    factory.return_value = stub
    app.run().button(key="run_search").click().run()
    assert not app.exception and not app.metric
    assert any("No complete usable forecasts" in w.value for w in app.warning)
    assert any(searcher.MESSAGES[code] in w.value for w in app.warning)
    assert all("never-show" not in w.value for w in app.warning)
    assert app.dataframe[0].value["Score / 100"].isna().all()


def test_reference_file_failure_displays_guidance(ui, monkeypatch):
    app, _, _, _, _, factory = ui
    monkeypatch.setattr(
        searcher,
        "load_destinations",
        Mock(side_effect=searcher.CatalogError("bad file")),
    )
    app.run()
    assert not app.exception and not factory.called
    assert "reference files" in app.error[0].value
