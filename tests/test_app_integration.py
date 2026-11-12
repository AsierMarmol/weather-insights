"""P4.3 complete user journeys; fake HTTP and temporary persistence only."""

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
    monkeypatch.setattr(WeatherService, "from_environment", factory)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    yield app, service, session, clock, factory
    assert all(p.read_bytes() == contents for p, contents in data.items())


def dashboard(app):
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception


def search_page(app):
    app.sidebar.radio[0].set_value("Searcher").run()
    assert not app.exception


def charts(app):
    return [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]


def test_metric_persists_across_navigation(journey):
    app, service, session, _, factory = journey
    app.run().button(key="run_search").click().run()
    saved = service.store.path.read_bytes()
    dashboard(app)
    app.radio(key="dashboard_metric").set_value("max_wind_kmh").run()
    app.multiselect(key="dashboard_destinations").select(TOLEDO.city_id).run()
    search_page(app)
    dashboard(app)
    assert app.radio(key="dashboard_metric").value == "max_wind_kmh"
    assert app.multiselect(key="dashboard_destinations").value == [
        TOLEDO.city_id
    ]
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
    assert charts(app)[0]["data"][0]["y"] == ["1. Seville"]


def test_all_windows_share_rows_and_do_not_refetch_on_navigation(journey):
    app, service, session, _, factory = journey
    app.run()
    dashboard(app)
    assert not charts(app) and not factory.called
    search_page(app)
    for days in range(1, 6):
        app.select_slider(key="_trip_days").set_value(days).run()
        app.button(key="run_search").click().run()
        assert not app.exception
        rows = app.session_state.search_analysis_rows
        snapshot = service.store.path.read_bytes()
        assert all(r["evaluated_periods"] == days * 3 for r in rows)
        dashboard(app)
        figures = charts(app)
        assert len(figures) == 3
        for figure, field in zip(
            figures,
            [
                "final_score",
                "mean_temperature_c",
                "all_preferences_pct",
            ],
        ):
            assert figure["data"][0]["x"] == pytest.approx(
                [r[field] for r in rows]
            )
        assert service.store.path.read_bytes() == snapshot
        search_page(app)
    assert len(session.calls) == 3 and factory.call_count == 1
    assert len(service.store.load()) == 120


def test_edited_preferences_keep_old_snapshot_until_new_search(journey):
    app, service, session, _, _ = journey
    app.run().button(key="run_search").click().run()
    original = app.session_state.search_analysis_rows
    saved = service.store.path.read_bytes()
    app.number_input(key="_trip_min").set_value(20.0).run()
    app.select_slider(key="_trip_days").set_value(5).run()
    dashboard(app)
    assert any("settings changed" in m.value for m in app.info)
    assert any("Preferences used: 16-24" in m.value for m in app.caption)
    assert charts(app)[0]["data"][0]["x"] == pytest.approx(
        [r["final_score"] for r in original]
    )
    search_page(app)
    app.button(key="run_search").click().run()
    updated = app.session_state.search_analysis_rows
    assert updated != original
    dashboard(app)
    assert not any("settings changed" in m.value for m in app.info)
    assert any("Preferences used: 20-24" in m.value for m in app.caption)
    assert all(r["days"] == 5 for r in updated)
    assert len(session.calls) == 3
    assert service.store.path.read_bytes() == saved


def test_new_search_resets_unavailable_dashboard_filter(journey):
    app, _, session, _, _ = journey
    app.run().button(key="run_search").click().run()
    dashboard(app)
    app.multiselect(key="dashboard_destinations").select(SEGOVIA.city_id).run()
    search_page(app)
    app.multiselect(key="_trip_activities").set_value(
        ["History and heritage"]
    ).run()
    app.button(key="run_search").click().run()
    dashboard(app)
    assert app.multiselect(key="dashboard_destinations").value == ["All"]
    assert len(charts(app)[0]["data"][0]["x"]) == 2
    assert len(session.calls) == 3


def test_partial_failure_and_recovery_use_one_service(journey):
    app, service, session, clock, factory = journey
    session.handler = catalog_handler(clock, failures={SEGOVIA.city_id: 404})
    app.run().button(key="run_search").click().run()
    assert len(session.calls) == 3 and len(service.store.load()) == 80
    dashboard(app)
    assert len(charts(app)[0]["data"][0]["x"]) == 2
    assert (
        "could not find"
        in app.dataframe[-1].value.iloc[0]["Why it is unavailable"]
    )
    session.handler = catalog_handler(clock)
    search_page(app)
    app.button(key="run_search").click().run()
    dashboard(app)
    assert len(charts(app)[0]["data"][0]["x"]) == 3
    assert len(session.calls) == 4 and len(service.store.load()) == 120
    assert factory.call_count == 1


def test_storage_failure_never_charts_unsaved_results(journey, monkeypatch):
    from weather_app.storage import StorageError

    app, service, session, _, _ = journey
    real_append = service.store.append
    monkeypatch.setattr(
        service.store,
        "append",
        Mock(side_effect=StorageError("Synthetic disk failure")),
    )
    app.run().button(key="run_search").click().run()
    assert service.unsaved_record_count == 40
    dashboard(app)
    assert not charts(app)
    assert all(
        "saved or read" in reason
        for reason in app.dataframe[-1].value["Why it is unavailable"]
    )
    assert len(session.calls) == 1
    monkeypatch.setattr(service.store, "append", real_append)
    search_page(app)
    app.button(key="run_search").click().run()
    dashboard(app)
    assert len(charts(app)) == 3 and service.unsaved_record_count == 0
    assert len(service.store.load()) == 160


def test_expired_results_warn_in_both_views_and_refresh_on_search(journey):
    app, service, session, clock, _ = journey
    app.run().button(key="run_search").click().run()
    clock.advance(hours=6)
    app.run()
    assert any("over three hours" in m.value for m in app.warning)
    dashboard(app)
    assert any("over three hours" in m.value for m in app.warning)
    assert len(session.calls) == 3
    search_page(app)
    app.button(key="run_search").click().run()
    dashboard(app)
    assert not any("over three hours" in m.value for m in app.warning)
    assert len(session.calls) == 6 and len(service.store.load()) == 240


def test_empty_new_search_clears_old_charts_without_fetching(journey):
    app, service, session, _, _ = journey
    app.run().button(key="run_search").click().run()
    saved = service.store.path.read_bytes()
    app.multiselect(key="_trip_activities").select("Urban experiences").run()
    app.multiselect(key="_trip_sizes").select("Small city or town").run()
    app.button(key="run_search").click().run()
    assert app.session_state.search_analysis_rows == []
    dashboard(app)
    assert not charts(app)
    assert any(
        "No destinations to show" in message.value for message in app.info
    )
    assert len(session.calls) == 3
    search_page(app)
    app.multiselect(key="_trip_activities").select("All").run()
    app.multiselect(key="_trip_sizes").select("All").run()
    app.button(key="run_search").click().run()
    dashboard(app)
    assert len(charts(app)) == 3 and len(session.calls) == 3
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
    service.store.path.write_bytes(original.read_bytes())
    saved = service.store.path.read_bytes()
    # Replay the existing genuine snapshot at its original retrieval window.
    clock.now = datetime.fromisoformat("2026-11-12T11:34:00+00:00")
    app.run().button(key="run_search").click().run()
    assert not app.exception and not session.calls
    scores = [float(metric.value) for metric in app.metric[::3]]
    assert scores == [83.9, 50.8, 46.9]
    dashboard(app)
    ranking, comparison, suitable = charts(app)
    assert ranking["data"][0]["y"] == [
        "1. Seville",
        "2. Toledo",
        "3. Segovia",
    ]
    rows = app.session_state.search_analysis_rows
    assert comparison["data"][0]["x"] == pytest.approx(
        [row["mean_temperature_c"] for row in rows]
    )
    assert suitable["data"][0]["x"] == pytest.approx(
        [row["all_preferences_pct"] for row in rows]
    )
    assert factory.call_count == 1 and not session.calls
    assert service.store.path.read_bytes() == saved
