"""Offline tests for the P4.2 Dashboard.

Most analysis rows below are SYNTHETIC inputs shaped like the P2.4 result
contract, using the PHASE2_SCOPE.md worked-example scores; catalog rows are
the real reference rows. ``test_genuine_p25_results_*`` replays the genuine
P2.5 forecasts saved in data/weather through the real analytics engine.
Nothing here fetches weather or writes data.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
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
from weather_app.analytics import analyse_destinations
from weather_app.dashboard import (
    ALL,
    DashboardDataError,
    all_preferences_chart,
    comparison_chart,
    filter_frame,
    prepare_frame,
    ranking_chart,
    search_context,
)
from weather_app.models import SearchPreferences
from weather_app.service import WeatherService
from weather_app.storage import (
    WEATHER_RECORDS_PATH,
    WeatherStore,
    load_destinations,
)

UTC = timezone.utc
RUN_AT = "2026-11-11T18:30:00+00:00"
RUN_AT_DT = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
# Toledo, Segovia, Seville, Barcelona
CITY_IDS = ("ES-45168", "ES-40194", "ES-41091", "ES-08019")
PREFERENCES = SearchPreferences(
    days=1,
    temperature_min_c=16,
    temperature_max_c=24,
    max_precipitation_probability_pct=30,
    max_wind_kmh=25,
)


def _available(city_id, passes, suitable, penalty, mean_t, max_p, max_w,
               retrieved=RUN_AT):
    match = 100 * sum(passes) / 9
    return {
        "city_id": city_id, "status": "available", "reason": None,
        "run_at_utc": RUN_AT, "days": 1,
        "forecast_retrieved_at_utc": retrieved,
        "expected_periods": 3, "evaluated_periods": 3,
        "temperature_passes": passes[0],
        "precipitation_passes": passes[1],
        "wind_passes": passes[2],
        "weather_match_pct": match, "travel_penalty": penalty,
        "final_score": max(match - penalty, 0),
        "suitable_period_count": suitable,
        "all_preferences_pct": 100 * suitable / 3,
        "mean_temperature_c": mean_t,
        "max_precipitation_probability_pct": max_p,
        "max_wind_kmh": max_w,
    }


def _unavailable(city_id, reason="fetch_failed"):
    row = {
        name: None
        for name in (
            "temperature_passes", "precipitation_passes", "wind_passes",
            "weather_match_pct", "travel_penalty", "final_score",
            "suitable_period_count", "all_preferences_pct",
            "mean_temperature_c", "max_precipitation_probability_pct",
            "max_wind_kmh",
        )
    }
    row.update(
        city_id=city_id, status="unavailable", reason=reason,
        run_at_utc=RUN_AT, days=1, forecast_retrieved_at_utc=None,
        expected_periods=3, evaluated_periods=0,
    )
    return row


def analysis_rows():
    """Worked example in shared order, plus one unavailable city."""
    return [
        _available("ES-45168", (3, 3, 3), 3, 61 / 60, 20.0, 30.0, 25.0,
                   retrieved="2026-11-11T17:00:00+00:00"),
        _available("ES-40194", (2, 2, 2), 0, 75 / 60, 65 / 3, 31.0, 26.0),
        _available("ES-41091", (2, 2, 2), 2, 5.0, 65 / 3, 31.0, 26.0),
        _unavailable("ES-08019"),
    ]


@pytest.fixture(scope="module")
def catalog_rows():
    rows = [
        d.as_catalog_row()
        for d in load_destinations()
        if d.city_id in CITY_IDS
    ]
    assert len(rows) == 4
    return rows


@pytest.fixture
def frame(catalog_rows):
    return prepare_frame(analysis_rows(), catalog_rows)


@pytest.fixture
def fresh_clock(monkeypatch):
    """Pretend 'now' is shortly after the synthetic search."""
    now = RUN_AT_DT + timedelta(minutes=10)
    monkeypatch.setattr(searcher, "utc_now", lambda: now)
    return now


# --------------------------------------------------------------- helpers


def test_prepare_frame_keeps_shared_order_ranks_and_names(frame):
    assert frame["city_id"].tolist() == list(CITY_IDS)
    assert frame["destination"].tolist() == [
        "Toledo", "Segovia", "Seville", "Barcelona",
    ]
    assert frame["rank"].tolist()[:3] == [1, 2, 3]
    assert frame["rank"].isna().tolist() == [False, False, False, True]
    assert frame.loc[0, "final_score"] == pytest.approx(5939 / 60)
    assert frame.loc[1, "final_score"] == pytest.approx(200 / 3 - 1.25)
    assert frame.loc[2, "final_score"] == pytest.approx(200 / 3 - 5)
    assert frame.loc[0, "activities"] == (
        "History and heritage", "Food and gastronomy",
    )


def test_prepare_frame_does_not_re_sort_given_rows(catalog_rows):
    rows = analysis_rows()
    rows[0], rows[1] = rows[1], rows[0]  # the engine's order is final
    reordered = prepare_frame(rows, catalog_rows)
    assert reordered["destination"].tolist()[:2] == ["Segovia", "Toledo"]
    assert reordered["rank"].tolist()[:2] == [1, 2]


def _broken(change):
    rows = analysis_rows()
    change(rows)
    return rows


@pytest.mark.parametrize("change, message", [
    (lambda r: r[0].pop("final_score"), "lacks final_score"),
    (lambda r: r[0].update(city_id="ES-99999"), "not in the catalog"),
    (lambda r: r[1].update(city_id="ES-45168"), "repeats"),
    (lambda r: r[0].update(final_score=None), "invalid final_score"),
    (lambda r: r[0].update(mean_temperature_c=float("nan")),
     "invalid mean_temperature_c"),
    (lambda r: r[0].update(evaluated_periods=True),
     "invalid evaluated_periods"),
    (lambda r: r[0].update(status="ranked"), "unknown status"),
    (lambda r: r[3].update(reason=None), "no reason"),
    (lambda r: r[1].update(run_at_utc="2026-11-11T19:30:00+00:00"),
     "more than one search"),
    (lambda r: r[1].update(days=2), "more than one search"),
    (lambda r: r[0].update(run_at_utc="2026-11-11T18:30:00"),
     "UTC timestamp"),
    (lambda r: r[0].update(forecast_retrieved_at_utc="yesterday"),
     "valid ISO"),
])
def test_prepare_frame_rejects_rows_outside_contract(
    catalog_rows, change, message
):
    with pytest.raises(DashboardDataError, match=message):
        prepare_frame(_broken(change), catalog_rows)


@pytest.mark.parametrize("kwargs, expected", [
    ({}, ["Toledo", "Segovia", "Seville", "Barcelona"]),
    ({"activities": [ALL]}, ["Toledo", "Segovia", "Seville", "Barcelona"]),
    ({"activities": ["Urban experiences"]}, ["Seville", "Barcelona"]),
    ({"activities": ["Coast", "Food and gastronomy"]},
     ["Toledo", "Segovia", "Seville", "Barcelona"]),
    ({"sizes": ["Small city or town"]}, ["Toledo", "Segovia"]),
    ({"activities": ["Urban experiences"], "sizes": ["Large city"]},
     ["Seville", "Barcelona"]),
    ({"activities": ["Urban experiences"],
      "sizes": ["Small city or town"]}, []),
    ({"destinations": ["ES-41091", "ES-45168"]}, ["Toledo", "Seville"]),
    ({"destinations": ["ES-41091"], "activities": ["Coast"]}, []),
])
def test_filter_frame_any_within_and_between_groups(frame, kwargs, expected):
    assert filter_frame(frame, **kwargs)["destination"].tolist() == expected


def test_search_context_reports_window_and_forecast_age(frame):
    context = search_context(frame)
    assert context["run_at_utc"] == RUN_AT_DT
    assert context["window_end_utc"] == RUN_AT_DT + timedelta(hours=24)
    assert context["oldest_retrieved_at_utc"] == datetime(
        2026, 11, 11, 17, 0, tzinfo=UTC
    )
    assert context["newest_retrieved_at_utc"] == RUN_AT_DT
    assert context["oldest_age"] == timedelta(minutes=90)
    assert search_context(frame.iloc[0:0]) is None


# ---------------------------------------------------------------- charts


def test_ranking_chart_plots_final_scores_in_shared_order(frame):
    figure = ranking_chart(frame)
    bar = figure.data[0]
    # Unavailable Barcelona is not plotted as a zero score.
    assert list(bar.y) == ["1. Toledo", "2. Segovia", "3. Seville"]
    assert list(bar.x) == pytest.approx(
        [5939 / 60, 200 / 3 - 1.25, 200 / 3 - 5]
    )
    assert "points" in figure.layout.xaxis.title.text
    assert figure.layout.yaxis.autorange == "reversed"


@pytest.mark.parametrize("metric, values, unit", [
    ("mean_temperature_c", [20.0, 65 / 3, 65 / 3], "°C"),
    ("max_precipitation_probability_pct", [30.0, 31.0, 31.0], "%"),
    ("max_wind_kmh", [25.0, 26.0, 26.0], "km/h"),
])
def test_comparison_chart_plots_metric_with_units(
    frame, metric, values, unit
):
    figure = comparison_chart(frame, metric)
    assert list(figure.data[0].x) == pytest.approx(values)
    assert unit in figure.layout.xaxis.title.text


def test_comparison_chart_marks_user_preferences(frame):
    temperature = comparison_chart(frame, "mean_temperature_c", PREFERENCES)
    band = temperature.layout.shapes[0]
    assert (band.x0, band.x1) == (16, 24)
    wind = comparison_chart(frame, "max_wind_kmh", PREFERENCES)
    assert wind.layout.shapes[0].x0 == wind.layout.shapes[0].x1 == 25
    assert comparison_chart(frame, "max_wind_kmh").layout.shapes == ()
    with pytest.raises(ValueError):
        comparison_chart(frame, "humidity_pct")


def test_all_preferences_chart_shows_share_and_counts(frame):
    bar = all_preferences_chart(frame).data[0]
    assert list(bar.x) == pytest.approx([100.0, 0.0, 200 / 3])
    assert list(bar.text) == ["3/3 periods", "0/3 periods", "2/3 periods"]


# ---------------------------------------------------------------- views


def _dashboard_script(rows, catalog, preferences, current, errors):
    import streamlit as st

    from weather_app.dashboard import render_dashboard

    state = st.session_state
    if preferences is not None and "search_result_preferences" not in state:
        state.search_result_preferences = preferences
        state.search_preferences = current or preferences
        state.search_errors = errors
    render_dashboard(rows, catalog)


def _app(rows, catalog, preferences=PREFERENCES, current=None, errors=None):
    app = AppTest.from_function(
        _dashboard_script,
        args=(rows, catalog, preferences, current, errors or {}),
        default_timeout=30,
    )
    return app.run()


def _texts(elements):
    return " ".join(element.value for element in elements)


def _specs(app):
    return [json.loads(c.proto.spec) for c in app.get("plotly_chart")]


def _titles(app):
    return [spec["layout"]["title"]["text"] for spec in _specs(app)]


def test_dashboard_without_rows_explains_what_to_do(catalog_rows):
    app = _app([], catalog_rows)
    assert not app.exception
    assert "No destinations to show" in _texts(app.info)
    assert not app.get("plotly_chart")


def test_dashboard_renders_three_analyses(catalog_rows, fresh_clock):
    app = _app(analysis_rows(), catalog_rows)
    assert not app.exception
    for key in ("dashboard_destinations", "dashboard_activities",
                "dashboard_sizes"):
        assert app.multiselect(key=key).value == [ALL]  # visible default
    assert _titles(app) == [
        "Suitability ranking: final score by destination",
        "Mean daytime temperature across destinations",
        "Daytime forecast periods meeting all three preferences",
    ]
    captions = _texts(app.caption)
    assert "Showing 3 ranked and 1 unavailable destination(s)." in captions
    assert "next 1 day(s)" in captions and "Europe/Madrid" in captions
    assert "oldest was 1 h 30 min old at search time" in captions
    assert "Preferences used: 16-24 °C" in captions
    assert not app.warning  # forecasts are fresh at the patched clock
    assert not app.info  # results match the current settings
    tables = [table.value for table in app.dataframe]
    assert tables[0]["Rank"].tolist() == [1, 2, 3]
    assert tables[-1]["Destination"].tolist() == ["Barcelona"]
    assert tables[-1]["Why it is unavailable"].tolist() == [
        searcher.MESSAGES["fetch_failed"]
    ]


def test_service_error_code_explains_unavailable_city(catalog_rows):
    app = _app(
        analysis_rows(), catalog_rows, errors={"ES-08019": "rate_limited"}
    )
    reasons = app.dataframe[-1].value["Why it is unavailable"].tolist()
    assert reasons == [searcher.MESSAGES["rate_limited"]]


def test_old_forecasts_and_changed_settings_are_flagged(catalog_rows):
    changed = SearchPreferences(
        days=3, temperature_min_c=10, temperature_max_c=18,
        max_precipitation_probability_pct=30, max_wind_kmh=25,
    )
    # Real clock: the synthetic forecasts are far older than three hours.
    app = _app(analysis_rows(), catalog_rows, current=changed)
    assert "over three hours ago" in _texts(app.warning)
    assert "settings changed after this search" in _texts(app.info)
    assert "Preferences used: 16-24 °C" in _texts(app.caption)


def test_filters_narrow_view_without_touching_search_state(
    catalog_rows, fresh_clock
):
    app = _app(analysis_rows(), catalog_rows)
    activities = app.multiselect(key="dashboard_activities")
    activities.select("Urban experiences").run()
    assert app.multiselect(key="dashboard_activities").value == [
        "Urban experiences"
    ]  # choosing a value clears All
    assert "Showing 1 ranked and 1 unavailable" in _texts(app.caption)
    assert app.dataframe[0].value["Destination"].tolist() == ["Seville"]
    assert app.dataframe[0].value["Rank"].tolist() == [3]  # shared rank

    app.multiselect(key="dashboard_sizes").select("Small city or town").run()
    assert "No destinations match these dashboard filters" in _texts(
        app.warning
    )
    assert not app.get("plotly_chart")

    app.multiselect(key="dashboard_activities").select(ALL).run()
    assert app.multiselect(key="dashboard_activities").value == [ALL]
    assert "Showing 2 ranked and 0 unavailable" in _texts(app.caption)
    assert app.session_state["search_preferences"] == PREFERENCES
    assert app.session_state["search_result_preferences"] == PREFERENCES
    assert "search_analysis_rows" not in app.session_state


def test_destination_filter_and_metric_choice(catalog_rows, fresh_clock):
    app = _app(analysis_rows(), catalog_rows)
    destinations = app.multiselect(key="dashboard_destinations")
    destinations.select("ES-45168").select("ES-08019").run()
    assert "Showing 1 ranked and 1 unavailable" in _texts(app.caption)

    app.radio(key="dashboard_metric").set_value("max_wind_kmh").run()
    assert "Strongest daytime wind across destinations" in _titles(app)
    spec = _specs(app)[1]
    assert spec["layout"]["xaxis"]["title"]["text"] == (
        "Highest period wind speed (km/h)"
    )
    assert spec["data"][0]["x"] == [25.0]


def test_only_unavailable_destinations_show_explicit_state(catalog_rows):
    rows = [_unavailable("ES-45168", "stale_forecast"),
            _unavailable("ES-08019")]
    app = _app(rows, catalog_rows, preferences=None)
    assert not app.exception
    assert "has a complete forecast to chart" in _texts(app.info)
    assert app.dataframe[-1].value["Why it is unavailable"].tolist() == [
        searcher.MESSAGES["stale_forecast"],
        searcher.MESSAGES["fetch_failed"],
    ]


def test_invalid_results_show_safe_error_not_traceback(catalog_rows):
    rows = analysis_rows()
    rows[0]["city_id"] = "ES-99999"
    app = _app(rows, catalog_rows)
    assert not app.exception
    assert "could not be displayed" in app.error[0].value
    assert "ES-99999" not in app.error[0].value


# ------------------------------------------------- page and genuine data


def _page_script(rows):
    import streamlit as st

    from weather_app.dashboard import render_dashboard_page

    if rows is not None and "search_analysis_rows" not in st.session_state:
        st.session_state.search_analysis_rows = rows
    render_dashboard_page()


def test_page_before_any_search_points_to_searcher():
    app = AppTest.from_function(_page_script, args=(None,)).run()
    assert not app.exception
    assert "Open the Searcher" in _texts(app.info)


def test_page_with_empty_search_result(catalog_rows):
    app = AppTest.from_function(_page_script, args=([],)).run()
    assert "No destinations to show" in _texts(app.info)


# Genuine P2.5 forecast groups (see PHASE2_SCOPE.md, P2.5 verification).
P25_FORECASTS = {
    "ES-45168": "5f188094-18a9-471c-9155-81a82d6caae3",
    "ES-40194": "93c655ea-1a12-4b06-bb42-cda59497238c",
    "ES-41091": "9bb6a9d5-dd22-482d-ae30-85db8ed1b51b",
}
P25_RUN_AT = datetime.fromisoformat("2026-11-12T11:29:04.669987+00:00")


@pytest.fixture(scope="module")
def genuine_rows():
    before = WEATHER_RECORDS_PATH.read_bytes()
    records = WeatherStore().load()
    forecasts = {
        city: [r for r in records if r.fetch_id == fetch_id]
        for city, fetch_id in P25_FORECASTS.items()
    }
    places = [d for d in load_destinations() if d.city_id in P25_FORECASTS]
    preferences = SearchPreferences(
        days=3, temperature_min_c=16, temperature_max_c=24,
        max_precipitation_probability_pct=30, max_wind_kmh=25,
    )
    rows = analyse_destinations(places, forecasts, preferences, P25_RUN_AT)
    assert WEATHER_RECORDS_PATH.read_bytes() == before
    return rows


def test_genuine_p25_results_drive_the_charts(genuine_rows, monkeypatch):
    monkeypatch.setattr(
        searcher, "utc_now", lambda: P25_RUN_AT + timedelta(minutes=5)
    )
    before = WEATHER_RECORDS_PATH.read_bytes()
    app = AppTest.from_function(
        _page_script, args=(genuine_rows,), default_timeout=30
    ).run()
    assert not app.exception
    ranking, comparison, suitable = _specs(app)
    assert ranking["data"][0]["y"] == [
        "1. Seville", "2. Toledo", "3. Segovia",
    ]
    # Independent tally from the P2.5 evidence: 24/27, 14/27, 13/27 checks.
    assert ranking["data"][0]["x"] == pytest.approx([
        100 * 24 / 27 - 5, 100 * 14 / 27 - 61 / 60, 100 * 13 / 27 - 75 / 60,
    ])
    # Charts plot exactly the engine's genuine statistics, in rank order.
    assert comparison["data"][0]["x"] == pytest.approx(
        [r["mean_temperature_c"] for r in genuine_rows]
    )
    assert suitable["data"][0]["x"] == pytest.approx(
        [r["all_preferences_pct"] for r in genuine_rows]
    )
    assert "next 3 day(s)" in _texts(app.caption)
    assert not app.warning
    assert WEATHER_RECORDS_PATH.read_bytes() == before  # display only


# ------------------------------------------------ end-to-end through app.py


def test_app_search_then_dashboard_reuses_results(monkeypatch, tmp_path):
    """Searcher saves once; the Dashboard only displays those results."""
    def blocked(*args, **kwargs):
        raise AssertionError("Tests must never make live HTTP requests")

    monkeypatch.setattr(requests.Session, "request", blocked)
    genuine = WEATHER_RECORDS_PATH.read_bytes()
    seville = CATALOG["ES-41091"]
    places = [TOLEDO, SEGOVIA, seville]
    clock = Clock(datetime(2026, 11, 12, 6, tzinfo=UTC))
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "weather.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    monkeypatch.setattr(searcher, "load_destinations", lambda: places)
    monkeypatch.setattr(searcher, "utc_now", clock)
    monkeypatch.setattr(
        WeatherService, "from_environment", Mock(return_value=service)
    )
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py"), default_timeout=30)

    app.run().button(key="run_search").click().run()
    assert not app.exception
    rows = app.session_state["search_analysis_rows"]
    calls, saved = len(session.calls), store.path.read_bytes()

    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception
    ranked = [r for r in rows if r["status"] == "available"]
    names = {d.city_id: d.city for d in places}
    assert _specs(app)[0]["data"][0]["y"] == [
        f"{i}. {names[r['city_id']]}" for i, r in enumerate(ranked, 1)
    ]
    assert _specs(app)[0]["data"][0]["x"] == pytest.approx(
        [r["final_score"] for r in ranked]
    )
    app.multiselect(key="dashboard_sizes").select("Large city").run()
    app.sidebar.radio[0].set_value("Searcher").run()
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert app.multiselect(key="dashboard_sizes").value == ["Large city"]
    assert "Showing 1 ranked" in _texts(app.caption)  # Seville only
    # Viewing and filtering made no requests and wrote no records.
    assert len(session.calls) == calls
    assert store.path.read_bytes() == saved
    assert WEATHER_RECORDS_PATH.read_bytes() == genuine
