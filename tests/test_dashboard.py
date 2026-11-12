"""P4.4 tests for the independent Dashboard.

Analysis rows built here and every fetched forecast are SYNTHETIC test
inputs (fake HTTP, temporary stores). Catalog rows are the real reference
rows. ``test_genuine_*`` reads a temporary copy of the genuine weather CSV.
No test makes a live request or writes to data/.
"""

from __future__ import annotations

import csv
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
from weather_app.client import AuthenticationError
from weather_app.config import load_product_defaults
from weather_app.dashboard import (
    ALL,
    MAP_SCALE,
    NO_DATA_COLOUR,
    DashboardDataError,
    all_preferences_chart,
    comparison_chart,
    filter_frame,
    map_figure,
    map_points,
    overview_preferences,
    prepare_frame,
    search_context,
    weather_ranks,
    weather_score_chart,
)
from weather_app.models import SearchPreferences
from weather_app.service import WeatherService
from weather_app.storage import StorageError, WeatherStore, load_destinations

ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
NOW = datetime(2026, 11, 12, 6, tzinfo=UTC)  # autumn: 16-24 °C
RUN_AT = "2026-11-11T18:30:00+00:00"
RUN_AT_DT = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
SEVILLE = CATALOG["ES-41091"]
CATALOG_ROWS = [d.as_catalog_row() for d in load_destinations()]
CATALOG_BY_NAME = {row["city"]: row["city_id"] for row in CATALOG_ROWS}
DEFAULTS = load_product_defaults()
PREFERENCES = SearchPreferences(
    days=1,
    temperature_min_c=16,
    temperature_max_c=24,
    max_precipitation_probability_pct=30,
    max_wind_kmh=25,
)


# ------------------------------------------------------------ row fixtures


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
    """Engine-style rows in TRIP order (Toledo first, Seville penalised).

    Segovia and Seville have identical weather (6/9 checks) but very
    different driving times; the Dashboard must tie them on weather alone.
    """
    return [
        _available("ES-45168", (3, 3, 3), 3, 61 / 60, 20.0, 30.0, 25.0,
                   retrieved="2026-11-11T17:00:00+00:00"),
        _available("ES-40194", (2, 2, 2), 0, 75 / 60, 65 / 3, 31.0, 26.0),
        _available("ES-41091", (2, 2, 2), 2, 5.0, 65 / 3, 31.0, 26.0),
        _unavailable("ES-08019"),
    ]


@pytest.fixture
def frame():
    return prepare_frame(analysis_rows(), CATALOG_ROWS)


# ------------------------------------------------------ criteria and ranks


@pytest.mark.parametrize("month, low, high", [
    (1, 10, 18), (4, 18, 26), (7, 22, 30), (10, 16, 24),
])
def test_overview_criteria_use_seasonal_defaults(month, low, high):
    prefs = overview_preferences(NOW.replace(month=month), DEFAULTS, 3)
    assert (prefs.temperature_min_c, prefs.temperature_max_c) == (low, high)
    assert prefs.max_precipitation_probability_pct == 30
    assert prefs.max_wind_kmh == 25
    assert prefs.activities == prefs.destination_sizes == ()  # All


def test_overview_window_is_one_to_five_days_using_madrid_season():
    late_november_utc = datetime(2026, 11, 30, 23, 30, tzinfo=UTC)
    prefs = overview_preferences(late_november_utc, DEFAULTS, 5)
    assert prefs.days == 5 and prefs.temperature_min_c == 10  # December
    for days in range(1, 6):
        assert overview_preferences(NOW, DEFAULTS, days).days == days
    for days in (0, 6):
        with pytest.raises(ValueError):
            overview_preferences(NOW, DEFAULTS, days)


def test_weather_ranks_share_ties_and_ignore_driving():
    ranks = weather_ranks(analysis_rows())
    # Toledo 9/9; Segovia and Seville tie at 6/9 despite 75 vs 351 min.
    assert ranks == {"ES-45168": 1, "ES-40194": 2, "ES-41091": 2}
    rows = [
        {"city_id": "c", "status": "available", "weather_match_pct": 70.0},
        {"city_id": "b", "status": "available", "weather_match_pct": 50.0},
        {"city_id": "a", "status": "available", "weather_match_pct": 50.0},
        {"city_id": "d", "status": "available", "weather_match_pct": 49.9},
        {"city_id": "e", "status": "unavailable",
         "weather_match_pct": None},
    ]
    assert weather_ranks(rows) == {"c": 1, "b": 2, "a": 2, "d": 4}


def test_prepare_frame_orders_by_weather_rank_then_city_id(frame):
    assert frame["city_id"].tolist() == [
        "ES-45168", "ES-40194", "ES-41091", "ES-08019",
    ]
    assert frame["rank"].tolist()[:3] == [1, 2, 2]
    assert frame["rank"].isna().tolist() == [False, False, False, True]
    reversed_input = prepare_frame(analysis_rows()[::-1], CATALOG_ROWS)
    assert reversed_input["city_id"].tolist() == frame["city_id"].tolist()


def _broken(change):
    rows = analysis_rows()
    change(rows)
    return rows


@pytest.mark.parametrize("change, message", [
    (lambda r: r[0].pop("final_score"), "lacks final_score"),
    (lambda r: r[0].update(city_id="ES-99999"), "not in the catalog"),
    (lambda r: r[1].update(city_id="ES-45168"), "repeats"),
    (lambda r: r[0].update(weather_match_pct=None),
     "invalid weather_match_pct"),
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
def test_prepare_frame_rejects_rows_outside_contract(change, message):
    with pytest.raises(DashboardDataError, match=message):
        prepare_frame(_broken(change), CATALOG_ROWS)


@pytest.mark.parametrize("kwargs, expected", [
    ({}, ["Toledo", "Segovia", "Seville", "Barcelona"]),
    ({"activities": [ALL]}, ["Toledo", "Segovia", "Seville", "Barcelona"]),
    ({"activities": ["Urban experiences"]}, ["Seville", "Barcelona"]),
    ({"sizes": ["Small city or town"]}, ["Toledo", "Segovia"]),
    ({"activities": ["Urban experiences"], "sizes": ["Large city"]},
     ["Seville", "Barcelona"]),
    ({"activities": ["Urban experiences"],
      "sizes": ["Small city or town"]}, []),
    ({"destinations": ["ES-41091", "ES-45168"]}, ["Toledo", "Seville"]),
])
def test_filters_narrow_rows_without_changing_ranks(frame, kwargs, expected):
    shown = filter_frame(frame, **kwargs)
    assert shown["destination"].tolist() == expected
    original = dict(zip(frame["city_id"], frame["rank"]))
    for city, rank in zip(shown["city_id"], shown["rank"]):
        assert (rank is pd_na and original[city] is pd_na) or (
            rank == original[city]
        )


pd_na = prepare_frame(analysis_rows(), CATALOG_ROWS)["rank"].iloc[-1]


def test_search_context_reports_window_and_forecast_age(frame):
    context = search_context(frame)
    assert context["run_at_utc"] == RUN_AT_DT
    assert context["window_end_utc"] == RUN_AT_DT + timedelta(hours=24)
    assert context["oldest_age"] == timedelta(minutes=90)
    assert search_context(frame.iloc[0:0]) is None


# ------------------------------------------------------------------ map


def test_map_shows_all_83_destinations_before_loading():
    points = map_points(CATALOG_ROWS)
    assert len(points) == len(CATALOG_ROWS) == 83
    for point, place in zip(points, CATALOG_ROWS):
        assert (point["latitude"], point["longitude"]) == (
            place["latitude"], place["longitude"],
        )
        assert point["status"] == "not_loaded"
        assert point["rank"] is None
        assert point["mean_temperature_c"] is None
        assert place["city"] in point["hover"]
        assert ", ".join(place["activities"]) in point["hover"]
        assert "°C" not in point["hover"]
        assert "Weather rank" not in point["hover"]
    figure = map_figure(points)
    assert [trace.type for trace in figure.data] == ["scattergeo"] * 2
    assert sum(len(trace.lat) for trace in figure.data) == 83
    assert figure.data[1].marker.color == NO_DATA_COLOUR
    assert figure.data[1].name == "Weather not loaded"
    # The map is centred on the middle of the catalog coordinates (all in
    # mainland Spain), not on Plotly's fitbounds guess, which sat ~3° north.
    geo = figure.layout.geo
    assert geo.fitbounds in (None, False)
    assert geo.center.lat == pytest.approx(39.834, abs=0.01)
    assert geo.center.lon == pytest.approx(-2.938, abs=0.01)
    assert geo.projection.scale == MAP_SCALE
    assert all(35.8 < p["latitude"] < 43.9 for p in points)
    assert all(-9.4 < p["longitude"] < 3.4 for p in points)


def test_map_hover_shows_city_activities_temperature_rank_and_score(frame):
    errors = {"ES-08019": "rate_limited"}
    points = {
        p["city_id"]: p for p in map_points(CATALOG_ROWS, frame, errors)
    }
    assert len(points) == 83
    toledo = points["ES-45168"]
    assert toledo["status"] == "ranked"
    assert toledo["hover"] == (
        "<b>Toledo</b><br>Activities: History and heritage, Food and "
        "gastronomy<br>Average daytime temperature: 20.0 °C"
        "<br>Weather rank: 1 of 3<br>Weather score: 100.0%"
    )
    assert "Weather rank: 2 of 3" in points["ES-41091"]["hover"]
    assert "Weather score: 66.7%" in points["ES-40194"]["hover"]
    barcelona = points["ES-08019"]
    assert barcelona["status"] == "unavailable"
    assert searcher.MESSAGES["rate_limited"] in barcelona["hover"]
    assert "°C" not in barcelona["hover"]
    without_row = next(
        r["city_id"] for r in CATALOG_ROWS
        if r["city_id"] not in {row["city_id"] for row in analysis_rows()}
    )
    assert points[without_row]["status"] == "not_loaded"
    figure = map_figure(list(points.values()))
    ranked, grey = figure.data
    assert list(ranked.customdata) == ["ES-45168", "ES-40194", "ES-41091"]
    assert list(ranked.marker.color) == pytest.approx(
        [100.0, 200 / 3, 200 / 3]
    )
    assert len(ranked.lat) + len(grey.lat) == 83
    assert grey.name == "No weather rank"


def test_map_highlight_dims_but_never_removes_markers():
    points = map_points(CATALOG_ROWS)
    figure = map_figure(points, highlighted=["ES-45168"])
    grey = figure.data[1]
    assert len(grey.lat) == 83
    opacity = dict(zip(grey.customdata, grey.marker.opacity))
    assert opacity["ES-45168"] == 0.95
    assert sum(value == 0.2 for value in opacity.values()) == 82


# --------------------------------------------------------------- charts


def test_weather_score_chart_uses_weather_rank_without_driving(frame):
    figure = weather_score_chart(frame)
    bar = figure.data[0]
    assert list(bar.y) == ["1. Toledo", "2. Segovia", "2. Seville"]
    assert list(bar.x) == pytest.approx([100.0, 200 / 3, 200 / 3])
    assert "no driving penalty" in figure.layout.xaxis.title.text


@pytest.mark.parametrize("metric, values, unit, limit", [
    ("mean_temperature_c", [20.0, 65 / 3, 65 / 3], "°C",
     "(seasonal range 16-24 °C shaded)"),
    ("max_precipitation_probability_pct", [30.0, 31.0, 31.0], "%",
     "(limit 30% dashed)"),
    ("max_wind_kmh", [25.0, 26.0, 26.0], "km/h", "(limit 25 km/h dashed)"),
])
def test_comparison_chart_plots_metric_with_units(
    frame, metric, values, unit, limit
):
    figure = comparison_chart(frame, metric, PREFERENCES)
    assert list(figure.data[0].x) == pytest.approx(values)
    assert unit in figure.layout.xaxis.title.text
    assert figure.layout.shapes  # seasonal range or limit marked
    # Named in the title, where no bar can hide it (P5.4 visual check).
    assert figure.layout.title.text.endswith(limit)
    assert not figure.layout.annotations
    with pytest.raises(ValueError):
        comparison_chart(frame, "humidity_pct")


def test_all_conditions_chart_counts_three_hour_slots(frame):
    figure = all_preferences_chart(frame)
    bar = figure.data[0]
    assert list(bar.x) == pytest.approx([100.0, 0.0, 200 / 3])
    assert list(bar.text) == ["3/3 slots", "0/3 slots", "2/3 slots"]
    assert "Three-hour daytime slots" in figure.layout.title.text


# ------------------------------------------------- Dashboard page (83 cities)


HOT = {"ES-08019", "ES-41091", "ES-29067"}  # Barcelona, Seville, Málaga


def varied_handler(clock, failures=None):
    """Synthetic forecasts; HOT cities are 5 °C warmer than the rest."""
    base = catalog_handler(clock, failures=failures)
    by_coordinates = {(d.latitude, d.longitude): d for d in CATALOG.values()}

    def handle(url, params):
        response = base(url, params)
        if url.endswith("/forecast") and response.status_code == 200:
            coord = response._payload["city"]["coord"]
            place = by_coordinates.get((coord["lat"], coord["lon"]))
            if place is not None and place.city_id in HOT:
                for item in response._payload["list"]:
                    item["main"]["temp"] += 5
        return response

    return handle


@pytest.fixture
def page(monkeypatch, tmp_path):
    def blocked(*args, **kwargs):
        raise AssertionError("No live HTTP in Dashboard tests")

    monkeypatch.setattr(requests.Session, "request", blocked)
    genuine = {
        p: p.read_bytes() for p in (ROOT / "data").rglob("*") if p.is_file()
    }
    clock = Clock(NOW)
    session = FakeSession(handler=varied_handler(clock))
    store = WeatherStore(tmp_path / "weather.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    factory = Mock(return_value=service)
    monkeypatch.setattr(searcher, "utc_now", clock)
    monkeypatch.setattr(WeatherService, "from_environment", factory)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    app.run()
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception
    yield app, service, session, clock, factory
    assert all(p.read_bytes() == data for p, data in genuine.items())


def _specs(app):
    return [json.loads(c.proto.spec) for c in app.get("plotly_chart")]


def _texts(elements):
    return " ".join(element.value for element in elements)


def _markers(app):
    """city_id -> (trace name, hover text, lat, lon) from the map."""
    geo = _specs(app)[0]
    found = {}
    for trace in geo["data"]:
        for city, hover, lat, lon in zip(
            trace["customdata"], trace["hovertext"], trace["lat"],
            trace["lon"],
        ):
            found[city] = (trace["name"], hover, lat, lon)
    return found


# A load over a store with thousands of rows is slow on some Windows PCs:
# WeatherStore.latest_forecast re-reads the whole CSV for each of the 83
# cities (storage-owner defect recorded in PHASE5 P5.3/P5.4). Those loads
# get a longer AppTest limit so the test checks behaviour, not that cost.
LARGE_STORE_TIMEOUT = 240


def _load(app, timeout=None):
    app.button(key="dashboard_load").click().run(timeout=timeout)
    assert not app.exception


def test_page_shows_map_and_criteria_without_any_request(page):
    app, _, session, _, factory = page
    markers = _markers(app)
    assert len(markers) == 83
    for place in CATALOG_ROWS:
        name, _, lat, lon = markers[place["city_id"]]
        assert name == "Weather not loaded"
        assert (lat, lon) == (place["latitude"], place["longitude"])
    assert app.select_slider(key="dashboard_days").value == 3
    assert app.button(key="dashboard_load").label == "Load weather overview"
    captions = _texts(app.caption)
    assert "16-24 °C" in captions and "≤ 30%" in captions
    assert "≤ 25 km/h" in captions
    assert "All 83 destinations are shown without weather" in _texts(
        app.info
    )
    assert len(_specs(app)) == 1  # the map only
    # Page scrolling over the map must not zoom it away from Spain.
    map_config = json.loads(app.get("plotly_chart")[0].proto.config)
    assert map_config["scrollZoom"] is False
    assert not session.calls and not factory.called
    assert "search_analysis_rows" not in app.session_state


def test_load_ranks_all_destinations_by_weather_only(page):
    app, service, session, _, factory = page
    _load(app)
    assert len(session.calls) == 83 and factory.call_count == 1
    assert len(service.store.load()) == 83 * 40  # every response saved
    overview = app.session_state["dashboard_overview"]
    rows = {r["city_id"]: r for r in overview["rows"]}
    assert len(rows) == 83
    assert "83 of 83 destinations can be ranked" in _texts(app.markdown)
    markers = _markers(app)
    assert {name for name, *_ in markers.values()} == {"Weather score"}
    ranks = weather_ranks(overview["rows"])
    # 80 equal scores share rank 1; the warmer HOT cities share rank 81.
    assert sorted(set(ranks.values())) == [1, 81]
    assert {c for c, r in ranks.items() if r == 81} == HOT
    for city, (_, hover, _, _) in markers.items():
        row = rows[city]
        temperature = f"{row['mean_temperature_c']:.1f} °C"
        assert f"Average daytime temperature: {temperature}" in hover
        assert f"Weather rank: {ranks[city]} of 83" in hover
        assert f"Weather score: {row['weather_match_pct']:.1f}%" in hover
    _, weather, comparison, slots = _specs(app)
    labels = weather["data"][0]["y"]
    tied = [CATALOG_BY_NAME[label.split(". ", 1)[1]] for label in labels[:80]]
    assert tied == sorted(tied)  # city_id orders ties, not driving time
    assert all(label.startswith("81. ") for label in labels[80:])
    assert weather["data"][0]["x"] == pytest.approx(
        [rows[c]["weather_match_pct"] for c in tied]
        + [rows[CATALOG_BY_NAME[label.split(". ", 1)[1]]][
            "weather_match_pct"] for label in labels[80:]]
    )
    assert len(comparison["data"][0]["x"]) == len(slots["data"][0]["x"])


@pytest.mark.parametrize("days", [1, 2, 3, 4, 5])
def test_each_window_covers_three_slots_per_day(page, days):
    app, _, session, _, _ = page
    app.select_slider(key="dashboard_days").set_value(days).run()
    _load(app)
    rows = app.session_state["dashboard_overview"]["rows"]
    assert all(r["status"] == "available" for r in rows)
    assert all(
        r["evaluated_periods"] == r["expected_periods"] == 3 * days
        for r in rows
    )
    assert f"next {days} day(s)" in _texts(app.caption)
    assert len(session.calls) == 83


def test_refresh_and_other_windows_reuse_cache_without_new_saves(page):
    app, service, session, _, _ = page
    _load(app)
    saved = service.store.path.read_bytes()
    assert app.button(key="dashboard_load").label == (
        "Refresh weather overview"
    )
    _load(app)  # refresh within three hours
    for days in (1, 5):
        app.select_slider(key="dashboard_days").set_value(days).run()
        _load(app)
    assert len(session.calls) == 83
    assert service.store.path.read_bytes() == saved
    assert app.session_state["dashboard_overview"]["cached"] == 83


def test_hover_filters_and_navigation_make_no_requests(page):
    app, service, session, _, _ = page
    _load(app)
    saved = service.store.path.read_bytes()
    before = app.session_state["dashboard_overview"]
    app.multiselect(key="dashboard_activities").select("Coast").run()
    assert app.multiselect(key="dashboard_activities").value == ["Coast"]
    geo = _specs(app)[0]
    assert sum(len(t["lat"]) for t in geo["data"]) == 83  # none removed
    ranked = geo["data"][0]
    opacity = dict(zip(ranked["customdata"], ranked["marker"]["opacity"]))
    coast = {
        r["city_id"] for r in CATALOG_ROWS if "Coast" in r["activities"]
    }
    assert {c for c, o in opacity.items() if o > 0.5} == coast
    labels = _specs(app)[1]["data"][0]["y"]
    shown = {CATALOG_BY_NAME[label.split(". ", 1)[1]] for label in labels}
    assert shown == coast
    barcelona = next(lb for lb in labels if lb.endswith("Barcelona"))
    assert barcelona.startswith("81. ")  # global rank kept
    app.radio(key="dashboard_metric").set_value("max_wind_kmh").run()
    app.select_slider(key="dashboard_days").set_value(5).run()
    app.sidebar.radio[0].set_value("Searcher").run()
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception
    assert app.multiselect(key="dashboard_activities").value == ["Coast"]
    assert app.radio(key="dashboard_metric").value == "max_wind_kmh"
    assert app.select_slider(key="dashboard_days").value == 5
    assert app.session_state["dashboard_overview"] == before
    # The edited window does not relabel the 3-day overview as new.
    assert "Your settings have changed" in _texts(app.info)
    assert "next 3 day(s)" in _texts(app.caption)
    assert len(session.calls) == 83
    assert service.store.path.read_bytes() == saved


def test_views_keep_separate_state_but_share_service_and_cache(page):
    app, _, session, _, factory = page
    _load(app)
    dashboard_rows = app.session_state["dashboard_overview"]["rows"]
    app.sidebar.radio[0].set_value("Searcher").run()
    app.multiselect(key="_trip_sizes").select("Large city").run()
    app.button(key="run_search").click().run()
    assert not app.exception
    assert len(session.calls) == 83 and factory.call_count == 1  # cached
    search_rows = app.session_state["search_analysis_rows"]
    assert 0 < len(search_rows) < 83
    by_city = {r["city_id"]: r for r in dashboard_rows}
    for row in search_rows:  # same engine, same weather match
        assert row["weather_match_pct"] == (
            by_city[row["city_id"]]["weather_match_pct"]
        )
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert app.session_state["dashboard_overview"]["rows"] == dashboard_rows
    assert app.multiselect(key="dashboard_sizes").value == [ALL]
    assert len(_markers(app)) == 83


def test_partial_failure_keeps_every_marker_with_neutral_reason(page):
    app, _, session, clock, _ = page
    session.handler = varied_handler(clock, failures={SEGOVIA.city_id: 404})
    _load(app)
    assert "82 of 83 destinations can be ranked" in _texts(app.markdown)
    name, hover, _, _ = _markers(app)[SEGOVIA.city_id]
    assert name == "No weather rank"
    assert searcher.MESSAGES["location_not_found"] in hover
    assert "°C" not in hover and "Weather rank" not in hover
    assert len(_markers(app)) == 83
    assert app.dataframe[-1].value["Destination"].tolist() == ["Segovia"]
    session.handler = varied_handler(clock)
    _load(app)  # recovery fetches only the missing city
    assert len(session.calls) == 84
    assert "83 of 83" in _texts(app.markdown)


def test_failed_saves_never_rank_unsaved_weather(page, monkeypatch):
    app, service, session, _, _ = page
    real_append = service.store.append
    monkeypatch.setattr(
        service.store, "append",
        Mock(side_effect=StorageError("Synthetic disk failure")),
    )
    _load(app)
    assert len(session.calls) == 1  # a storage failure stops the batch
    assert "0 of 83 destinations can be ranked" in _texts(app.markdown)
    assert len(_specs(app)) == 1  # map only; no ranked charts
    markers = _markers(app)
    assert len(markers) == 83
    assert all(
        searcher.MESSAGES["storage"] in hover
        for _, hover, _, _ in markers.values()
    )
    monkeypatch.setattr(service.store, "append", real_append)
    _load(app)
    assert service.unsaved_record_count == 0
    assert "83 of 83" in _texts(app.markdown)
    # The kept first response is saved once on retry; its city is then
    # fetched again as a distinct response. Nothing is saved twice.
    assert len(session.calls) == 84
    assert len(service.store.load()) == 84 * 40


def test_missing_key_explains_setup_and_keeps_the_map(page):
    app, _, session, _, factory = page
    factory.side_effect = AuthenticationError(
        "OPENWEATHER_API_KEY is not set. Add it to variables.env."
    )
    _load(app)
    assert searcher.MESSAGES["authentication"] in _texts(app.error)
    assert "variables.env" in _texts(app.caption)
    assert len(_markers(app)) == 83 and not session.calls
    assert "dashboard_overview" not in app.session_state


def test_old_forecasts_warn_and_refresh_fetches_again(page):
    app, _, session, clock, _ = page
    _load(app)
    clock.advance(hours=4)
    app.run()
    assert "over three hours ago" in _texts(app.warning)
    _load(app, timeout=LARGE_STORE_TIMEOUT)  # store now holds 3,320 rows
    assert len(session.calls) == 166
    assert "over three hours ago" not in _texts(app.warning)


def test_summer_load_uses_summer_criteria(page):
    app, _, _, clock, _ = page
    clock.now = datetime(2026, 7, 10, 6, tzinfo=UTC)
    app.run()
    assert "22-30 °C" in _texts(app.caption)
    _load(app)
    used = app.session_state["dashboard_overview"]["preferences"]
    assert (used.temperature_min_c, used.temperature_max_c) == (22, 30)


GENUINE_CSV = ROOT / "data/weather/weather_records.csv"


def _genuine_lines(until):
    """Header plus genuine CSV lines retrieved at or before ``until``."""
    with GENUINE_CSV.open(newline="", encoding="utf-8") as file:
        header, *rows = list(csv.reader(file))
    when = header.index("retrieved_at_utc")
    kept = [
        row for row in rows
        if datetime.fromisoformat(row[when]) <= until
    ]
    return header, kept


def _write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def test_genuine_saved_forecasts_rank_without_requests(page):
    # Replay the P2.5 snapshot as it was at 11:34 UTC: only the 164 rows
    # saved by then (a temporary copy), not the later 12:36 collection.
    app, service, session, clock, _ = page
    clock.now = datetime.fromisoformat("2026-11-12T11:34:00+00:00")
    header, rows = _genuine_lines(clock.now)
    assert len(rows) == 164
    _write_csv(service.store.path, header, rows)
    _load(app)
    fetched = {
        (c["params"]["lat"], c["params"]["lon"])
        for c in session.calls if "lat" in c["params"]
    }
    for place in (TOLEDO, SEGOVIA, SEVILLE):  # reused genuine records
        assert (place.latitude, place.longitude) not in fetched
    rows = {
        r["city_id"]: r
        for r in app.session_state["dashboard_overview"]["rows"]
    }
    # Independent tally of nine genuine daytime slots (P2.5 evidence).
    for place, checks in ((SEVILLE, 24), (TOLEDO, 14), (SEGOVIA, 13)):
        assert rows[place.city_id]["weather_match_pct"] == pytest.approx(
            100 * checks / 27
        )
    hover = _markers(app)[SEVILLE.city_id][1]
    assert f"{rows[SEVILLE.city_id]['mean_temperature_c']:.1f} °C" in hover


# ------------------------------------------------ P5.4 acceptance additions

BARCELONA = "ES-08019"
# Last response of the accumulated 82-destination collection (PR #16).
SNAPSHOT = datetime.fromisoformat("2026-11-12T12:37:35.318886+00:00")


def _independent_tally(rows, header, until, days=3):
    """Weather score and mean temperature per city from the raw CSV text.

    Uses the latest forecast group per city retrieved by ``until``. In
    November Madrid daytime (09:00-18:00 CET) holds the 09/12/15 UTC
    slots. No WeatherRecord, zoneinfo or analytics code is used.
    """
    col = {name: i for i, name in enumerate(header)}
    groups = {}
    for row in rows:
        if row[col["kind"]] != "forecast":
            continue
        key = (row[col["city_id"]], row[col["fetch_id"]])
        groups.setdefault(key, []).append(row)
    latest = {}
    for (city, _), group in groups.items():
        retrieved = datetime.fromisoformat(group[0][col["retrieved_at_utc"]])
        if city not in latest or retrieved > latest[city][0]:
            latest[city] = (retrieved, group)
    end = until + timedelta(hours=24 * days)
    result = {}
    for city, (_, group) in latest.items():
        by_time = {
            datetime.fromisoformat(r[col["valid_at_utc"]]): r for r in group
        }
        slots = [
            t for t in sorted(by_time)
            if until < t <= end and t.hour in (9, 12, 15)
        ]
        assert len(slots) == 3 * days, city
        values = [
            (float(by_time[t][col["temperature_c"]]),
             float(by_time[t][col["precipitation_probability_pct"]]),
             float(by_time[t][col["wind_kmh"]]))
            for t in slots
        ]
        checks = sum(
            (16 <= t <= 24) + (p <= 30) + (w <= 25) for t, p, w in values
        )
        result[city] = (
            100 * checks / (3 * len(slots)),
            sum(v[0] for v in values) / len(values),
        )
    return result


def test_genuine_82_destination_snapshot_matches_independent_tally(page):
    # A temporary copy of every genuine row, replayed at the time of the
    # last saved response, so all 82 saved forecasts are fresh. Barcelona
    # has no genuine forecast; its request fails, so nothing synthetic is
    # ranked.
    app, service, session, clock, _ = page
    clock.now = SNAPSHOT
    session.handler = varied_handler(clock, failures={BARCELONA: 404})
    header, rows = _genuine_lines(SNAPSHOT)
    _write_csv(service.store.path, header, rows)
    _load(app, timeout=LARGE_STORE_TIMEOUT)

    barcelona = CATALOG[BARCELONA]
    assert [
        (c["params"]["lat"], c["params"]["lon"]) for c in session.calls
    ] == [(barcelona.latitude, barcelona.longitude)]
    assert len(service.store.load()) == len(rows)  # nothing new saved
    assert "82 of 83 destinations can be ranked" in _texts(app.markdown)

    expected = _independent_tally(rows, header, SNAPSHOT)
    assert len(expected) == 82 and BARCELONA not in expected
    want_rank = {
        city: 1 + sum(o[0] > score for o in expected.values())
        for city, (score, _) in expected.items()
    }
    got = {
        r["city_id"]: r
        for r in app.session_state["dashboard_overview"]["rows"]
    }
    markers = _markers(app)
    assert len(markers) == 83
    for city, (score, mean_t) in expected.items():
        assert got[city]["weather_match_pct"] == pytest.approx(score)
        assert got[city]["mean_temperature_c"] == pytest.approx(mean_t)
        name, hover, _, _ = markers[city]
        assert name == "Weather score"
        assert f"Average daytime temperature: {mean_t:.1f} °C" in hover
        assert f"Weather rank: {want_rank[city]} of 82" in hover
        assert f"Weather score: {score:.1f}%" in hover
    name, hover, _, _ = markers[BARCELONA]
    assert name == "No weather rank" and "°C" not in hover

    # Ranking chart: weather rank, then city_id within ties.
    order = sorted(expected, key=lambda c: (want_rank[c], c))
    names = {r["city_id"]: r["city"] for r in CATALOG_ROWS}
    weather = _specs(app)[1]["data"][0]
    assert weather["y"] == [f"{want_rank[c]}. {names[c]}" for c in order]
    assert weather["x"] == pytest.approx([expected[c][0] for c in order])


def test_charts_agree_with_their_tables(page):
    app, _, _, _, _ = page
    _load(app)
    _, weather, comparison, slots = _specs(app)
    ranking, compared, all_three = (d.value for d in app.dataframe[:3])
    labels = [
        f"{r}. {n}"
        for r, n in zip(ranking["Weather rank"], ranking["Destination"])
    ]
    assert weather["data"][0]["y"] == labels
    assert weather["data"][0]["x"] == pytest.approx(
        ranking["Weather score (%)"].tolist()
    )
    assert "no driving penalty" in weather["layout"]["xaxis"]["title"]["text"]
    columns = {
        "mean_temperature_c": "Average daytime temperature (°C)",
        "max_precipitation_probability_pct": (
            "Highest slot precipitation probability (%)"
        ),
        "max_wind_kmh": "Highest slot wind speed (km/h)",
    }
    for metric, column in columns.items():
        app.radio(key="dashboard_metric").set_value(metric).run()
        chart = _specs(app)[2]
        assert chart["data"][0]["y"] == labels
        assert chart["data"][0]["x"] == pytest.approx(
            compared[column].tolist()
        )
        assert chart["layout"]["xaxis"]["title"]["text"] == column
    assert slots["data"][0]["y"] == labels
    assert slots["data"][0]["x"] == pytest.approx(
        all_three["Share of slots (%)"].tolist()
    )
    assert slots["data"][0]["text"] == [
        f"{k}/{n} slots"
        for k, n in zip(
            all_three["Slots meeting all three"],
            all_three["Slots with data"],
        )
    ]
    assert set(all_three["Slots with data"]) == {9}  # 3 days x 3 slots


def test_empty_filter_states_keep_every_marker(page):
    app, _, session, clock, _ = page
    session.handler = varied_handler(clock, failures={SEGOVIA.city_id: 404})
    _load(app)
    app.multiselect(key="dashboard_destinations").select(
        SEGOVIA.city_id
    ).run()
    assert "None of the selected destinations has a complete forecast" in (
        _texts(app.info)
    )
    assert len(_specs(app)) == 1  # map only; no empty charts
    assert app.dataframe[-1].value["Destination"].tolist() == ["Segovia"]
    segovia_size = next(
        r["destination_size"] for r in CATALOG_ROWS
        if r["city_id"] == SEGOVIA.city_id
    )
    other = next(
        r["destination_size"] for r in CATALOG_ROWS
        if r["destination_size"] != segovia_size
    )
    app.multiselect(key="dashboard_sizes").select(other).run()
    assert "No destinations match these filters" in _texts(app.warning)
    assert sum(len(t["lat"]) for t in _specs(app)[0]["data"]) == 83
    assert len(session.calls) == 83
