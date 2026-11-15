"""P4.3/P4.4 complete user journeys; fake HTTP and temporary persistence only.

Since P4.4 the Dashboard is an independent weather overview with its own
window, Load/refresh action and state. These journeys check that the two
views share one service, cache and save path while never sharing results.
"""

import json
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

from weather_app import dashboard as dashboard_module
from weather_app import searcher
from weather_app.service import WeatherService
from weather_app.storage import WeatherStore

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 12, 6, tzinfo=timezone.utc)


@pytest.fixture
def journey(monkeypatch, tmp_path):
    def blocked(*args, **kwargs):
        raise AssertionError("No live HTTP in integration tests")

    monkeypatch.setattr(requests.Session, "request", blocked)
    data = {
        p: p.read_bytes() for p in (ROOT / "data").rglob("*") if p.is_file()
    }
    clock = Clock(NOW)
    places = [TOLEDO, SEGOVIA, CATALOG["ES-41091"]]
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "weather.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    factory = Mock(return_value=service)
    monkeypatch.setattr(searcher, "utc_now", clock)
    monkeypatch.setattr(searcher, "load_destinations", lambda: places)
    monkeypatch.setattr(dashboard_module, "load_destinations", lambda: places)
    monkeypatch.setattr(WeatherService, "from_environment", factory)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    # Reserve the load for each test's configured scenario.
    app.session_state.dashboard_attempted_days = 3
    app.session_state.view = "Searcher"
    yield app, service, session, clock, factory
    assert all(p.read_bytes() == contents for p, contents in data.items())


def dashboard(app):
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception


def load_dashboard(app):
    dashboard(app)
    app.button(key="dashboard_load").click().run()
    assert not app.exception


def search_page(app):
    app.sidebar.radio[0].set_value("Searcher").run()
    assert not app.exception


def charts(app):
    return [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]


def texts(elements):
    return " ".join(element.value for element in elements)


def overview(app):
    return app.session_state["dashboard_overview"]


def test_window_persists_across_navigation(journey):
    app, service, session, _, factory = journey
    app.run().button(key="run_search").click().run()
    saved = service.store.path.read_bytes()
    load_dashboard(app)  # reuses the Searcher's fresh forecasts
    app.selectbox(key="dashboard_days").set_value(5).run()
    search_page(app)
    dashboard(app)
    assert app.selectbox(key="dashboard_days").value == 5
    assert not app.multiselect
    assert len(session.calls) == 3 and factory.call_count == 1
    assert service.store.path.read_bytes() == saved


def test_all_selection_is_consistent_between_views(journey):
    app, _, session, _, _ = journey
    app.run().multiselect(key="_trip_activities").select(
        "History and heritage"
    ).run()
    assert app.multiselect(key="_trip_activities").value == [
        "History and heritage"
    ]
    assert app.session_state.search_preferences.activities == (
        "History and heritage",
    )
    app.multiselect(key="_trip_activities").select("All").run()
    assert app.multiselect(key="_trip_activities").value == ["All"]
    app.multiselect(key="_trip_activities").set_value([]).run()
    assert app.multiselect(key="_trip_activities").value == ["All"]
    app.multiselect(key="_trip_sizes").select("Large city").run()
    assert app.multiselect(key="_trip_sizes").value == ["Large city"]
    assert not session.calls
    app.button(key="run_search").click().run()
    assert len(session.calls) == 1
    dashboard(app)
    # Searcher filters never leak into the independent Dashboard.
    assert not app.multiselect
    assert len(charts(app)) == 1  # map only until the Dashboard loads
    assert "dashboard_overview" not in app.session_state
    assert len(session.calls) == 1


def test_all_windows_share_service_and_do_not_refetch(journey):
    app, service, session, _, factory = journey
    app.run()
    dashboard(app)
    assert len(charts(app)) == 1 and not factory.called  # map, no request
    search_page(app)
    for days in range(1, 6):
        app.selectbox(key="_trip_days").set_value(days).run()
        app.button(key="run_search").click().run()
        assert not app.exception
        search_rows = app.session_state.search_analysis_rows
        snapshot = service.store.path.read_bytes()
        dashboard(app)
        app.selectbox(key="dashboard_days").set_value(days).run()
        app.button(key="dashboard_load").click().run()
        assert not app.exception
        rows = overview(app)["rows"]
        assert all(r["evaluated_periods"] == days * 3 for r in rows)
        weather = {r["city_id"]: r["weather_match_pct"] for r in rows}
        for row in search_rows:  # same engine, same weather match
            assert weather[row["city_id"]] != row["weather_match_pct"]
        assert len(charts(app)) == 2
        assert service.store.path.read_bytes() == snapshot
        search_page(app)
    assert len(session.calls) == 3 and factory.call_count == 1
    assert len(service.store.load()) == 120


def test_edited_settings_keep_old_results_until_explicit_action(journey):
    app, service, session, _, _ = journey
    app.run().button(key="run_search").click().run()
    original = app.session_state.search_analysis_rows
    app.number_input(key="_trip_min").set_value(20.0).run()
    app.selectbox(key="_trip_days").set_value(5).run()
    assert "Settings changed" in texts(app.info)
    assert app.session_state.search_analysis_rows == original
    load_dashboard(app)
    loaded = overview(app)
    app.selectbox(key="dashboard_days").set_value(5).run()
    assert "Your settings have changed" not in texts(app.info)
    assert "next 5 day(s)" in texts(app.caption)
    assert overview(app) != loaded
    assert all(r["evaluated_periods"] == 15 for r in overview(app)["rows"])
    app.button(key="dashboard_load").click().run()
    assert "Your settings have changed" not in texts(app.info)
    assert all(r["evaluated_periods"] == 15 for r in overview(app)["rows"])
    # The Dashboard refresh did not touch the Searcher's snapshot.
    assert app.session_state.search_analysis_rows == original
    search_page(app)
    app.button(key="run_search").click().run()
    assert app.session_state.search_analysis_rows != original
    assert len(session.calls) == 3
    assert len(service.store.load()) == 120


def test_searches_never_change_unfiltered_dashboard(journey):
    app, _, session, _, _ = journey
    load_dashboard(app.run())
    loaded = overview(app)
    search_page(app)
    app.multiselect(key="_trip_activities").set_value(
        ["History and heritage"]
    ).run()
    app.button(key="run_search").click().run()
    assert len(app.session_state.search_analysis_rows) == 2
    dashboard(app)
    assert not app.multiselect
    assert overview(app) == loaded
    assert len(charts(app)[1]["data"][0]["x"]) == 3
    assert len(session.calls) == 3


def test_partial_failure_and_recovery_use_one_service(journey):
    app, service, session, clock, factory = journey
    session.handler = catalog_handler(clock, failures={SEGOVIA.city_id: 404})
    load_dashboard(app.run())
    assert len(session.calls) == 3 and len(service.store.load()) == 80
    assert "2 of 3 destinations can be ranked" in texts(app.markdown)
    assert len(charts(app)[1]["data"][0]["x"]) == 2
    assert "could not find" in (
        app.dataframe[-1].value.iloc[0]["Why it has no destination rank"]
    )
    session.handler = catalog_handler(clock)
    app.button(key="dashboard_load").click().run()
    assert len(charts(app)[1]["data"][0]["x"]) == 3
    assert len(session.calls) == 4 and len(service.store.load()) == 120
    search_page(app)
    app.button(key="run_search").click().run()  # reuses the same cache
    assert len(session.calls) == 4 and factory.call_count == 1


def test_storage_failure_never_charts_unsaved_results(journey, monkeypatch):
    from weather_app.storage import StorageError

    app, service, session, _, _ = journey
    real_append = service.store.append
    monkeypatch.setattr(
        service.store,
        "append",
        Mock(side_effect=StorageError("Synthetic disk failure")),
    )
    load_dashboard(app.run())
    assert service.unsaved_record_count == 40
    assert len(charts(app)) == 1  # the map, with no ranked markers
    assert all(
        "saved or read" in reason
        for reason in app.dataframe[-1].value["Why it has no destination rank"]
    )
    assert len(session.calls) == 1
    monkeypatch.setattr(service.store, "append", real_append)
    app.button(key="dashboard_load").click().run()
    assert len(charts(app)) == 2 and service.unsaved_record_count == 0
    # Recover the first response without requesting it twice.
    assert len(session.calls) == 3
    assert len(service.store.load()) == 120


def test_expired_results_warn_in_both_views_and_refresh_explicitly(journey):
    app, service, session, clock, _ = journey
    app.run().button(key="run_search").click().run()
    load_dashboard(app)
    clock.advance(hours=6)
    search_page(app)
    assert "over three hours" in texts(app.warning)
    dashboard(app)
    assert "over three hours ago" in texts(app.warning)
    assert len(session.calls) == 3
    app.button(key="dashboard_load").click().run()
    assert "over three hours ago" not in texts(app.warning)
    assert len(session.calls) == 6
    search_page(app)  # its own results are still the old snapshot
    assert "over three hours" in texts(app.warning)
    app.button(key="run_search").click().run()  # reuses fresh forecasts
    assert "over three hours" not in texts(app.warning)
    assert len(session.calls) == 6 and len(service.store.load()) == 240


def test_empty_new_search_keeps_dashboard_without_fetching(journey):
    app, service, session, _, _ = journey
    load_dashboard(app.run())
    loaded = overview(app)
    saved = service.store.path.read_bytes()
    search_page(app)
    app.multiselect(key="_trip_activities").select("Urban experiences").run()
    app.multiselect(key="_trip_sizes").select("Small city or town").run()
    app.button(key="run_search").click().run()
    assert app.session_state.search_analysis_rows == []
    dashboard(app)
    assert overview(app) == loaded and len(charts(app)) == 2
    assert len(session.calls) == 3
    assert service.store.path.read_bytes() == saved


def test_progress_reaches_completion_and_is_removed(journey, monkeypatch):
    app, _, _, _, _ = journey
    bar = Mock()
    create = Mock(return_value=bar)
    monkeypatch.setattr(searcher.st, "progress", create)
    app.run().button(key="run_search").click().run()
    assert not app.exception
    create.assert_called_once_with(0.0, text="Preparing your search…")
    assert [call.args[0] for call in bar.progress.call_args_list] == [
        1 / 3,
        2 / 3,
        1,
    ]
    bar.empty.assert_called_once()


def test_genuine_saved_data_drives_complete_app_without_requests(journey):
    app, service, session, clock, factory = journey
    original = ROOT / "data/weather/weather_records.csv"
    # Replay only records available at that historical time. New app use
    # must not replace this test's known forecast inputs with later issues.
    clock.now = datetime.fromisoformat("2026-11-12T11:34:00+00:00")
    historical = [r for r in WeatherStore(original).load()
                  if r.retrieved_at_utc <= clock.now]
    assert len(historical) == 164
    service.store.append(historical)  # Temporary store only.
    saved = service.store.path.read_bytes()
    app.run().button(key="run_search").click().run()
    assert not app.exception and not session.calls
    scores = card_scores(app)
    # Frozen CSV independently evaluated with preferred Low rain and
    # Moderate wind, 80/20 aggregation and two points per driving hour.
    assert scores == [74.0, 69.6, 67.1]
    load_dashboard(app)
    _, scatter = charts(app)
    rows = overview(app)["rows"]
    assert scatter["data"][0]["y"] == pytest.approx(
        [row["final_score"] for row in rows]
    )
    full = next(d.value for d in app.dataframe
                if "Driving distance (km)" in d.value.columns)
    assert full["Destination"].tolist() == ["Seville", "Toledo", "Segovia"]
    assert full["Temperature (°C)"].tolist() == pytest.approx(
        [row["mean_temperature_c"] for row in rows]
    )
    heat = next(e.proto.body for e in app.get('html')
                if 'class="wi-heatmap-table"' in e.proto.body)
    assert heat.count('scope="row"') == 3
    assert factory.call_count == 1 and not session.calls
    assert service.store.path.read_bytes() == saved


def card_scores(app):
    import re
    html = next(element.proto.body for element in app.get('html')
                if 'class="wi-trip-list"' in element.proto.body)
    return [float(value) for value in re.findall(
        r'class="wi-trip-fit">([0-9.]+)/100', html)]


def test_scoring_version_change_resets_results_but_preserves_service():
    app = AppTest.from_file(str(ROOT / "app.py"))
    app.session_state.scoring_version = "previous-formula"
    app.session_state.dashboard_attempted_days = 3
    app.session_state.dashboard_overview = {"preferences": None}
    app.session_state.search_results = ["obsolete"]
    app.session_state.service_unsaved = ["pending-recovery"]
    app.run()
    assert not app.exception
    assert "dashboard_attempted_days" not in app.session_state
    assert "dashboard_overview" not in app.session_state
    assert "search_results" not in app.session_state
    assert app.session_state.service_unsaved == ["pending-recovery"]
