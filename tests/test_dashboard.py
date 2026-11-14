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
from scoring_reference import reference_score
import requests
from streamlit.testing.v1 import AppTest
from weather_fakes import (
    CATALOG,
    SEGOVIA,
    TOLEDO,
    Clock,
    FakeSession,
    FakeResponse,
    catalog_handler,
    make_client,
)

from weather_app import searcher
from weather_app.client import AuthenticationError
from weather_app.config import (
    load_product_defaults, load_location_overrides,
)
from weather_app.dashboard import (
    MAP_ZOOM,
    MADRID_ORIGIN,
    OSM_TILE_URL,
    NO_DATA_COLOUR,
    DashboardDataError,
    map_figure,
    map_points,
    overview_preferences,
    prepare_frame,
    search_context,
    destination_ranks,
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
        "mean_precipitation_probability_pct": max_p / 2,
        "mean_wind_kmh": max_w / 2,
        "max_precipitation_probability_pct": max_p,
        "max_wind_kmh": max_w,
    }


def _unavailable(city_id, reason="fetch_failed"):
    row: dict[str, str | float | None] = {
        name: None
        for name in (
            "temperature_passes", "precipitation_passes", "wind_passes",
            "weather_match_pct", "travel_penalty", "final_score",
            "suitable_period_count", "all_preferences_pct",
            "mean_temperature_c", "mean_precipitation_probability_pct",
            "mean_wind_kmh", "max_precipitation_probability_pct",
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


def test_destination_ranks_include_driving_and_share_final_score_ties():
    ranks = destination_ranks(analysis_rows())
    # Toledo 9/9; Segovia and Seville tie at 6/9 despite 75 vs 351 min.
    assert ranks == {"ES-45168": 1, "ES-40194": 2, "ES-41091": 3}
    rows = [
        {"city_id": "c", "status": "available", "final_score": 70.0},
        {"city_id": "b", "status": "available", "final_score": 50.0},
        {"city_id": "a", "status": "available", "final_score": 50.0},
        {"city_id": "d", "status": "available", "final_score": 49.9},
        {"city_id": "e", "status": "unavailable",
         "final_score": None},
    ]
    assert destination_ranks(rows) == {"c": 1, "b": 2, "a": 2, "d": 4}


def test_prepare_frame_orders_by_weather_rank_then_city_id(frame):
    assert frame["city_id"].tolist() == [
        "ES-45168", "ES-40194", "ES-41091", "ES-08019",
    ]
    assert frame["rank"].tolist()[:3] == [1, 2, 3]
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


def test_search_context_reports_window_and_forecast_age(frame):
    context = search_context(frame)
    assert context is not None
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
        assert "Destination rank" not in point["hover"]
    figure = map_figure(points)
    traces = figure.to_plotly_json()["data"]
    assert [trace["type"] for trace in traces] == ["scattermap"] * 3
    assert sum(len(trace["lat"]) for trace in traces[:2]) == 83
    assert traces[1]["marker"]["color"] == NO_DATA_COLOUR
    assert traces[1]["name"] == "Weather not loaded"
    tile_map = figure.layout.map
    assert tile_map.center.lat == pytest.approx(39.834, abs=0.01)
    assert tile_map.center.lon == pytest.approx(-2.938, abs=0.01)
    assert tile_map.zoom == MAP_ZOOM
    assert tile_map.style['sources']['osm']['tiles'] == [OSM_TILE_URL]
    assert 'openstreetmap.org/copyright' in (
        tile_map.style['sources']['osm']['attribution'])
    origin = figure.to_plotly_json()["data"][2]
    assert list(origin["lat"]) == [MADRID_ORIGIN['lat']]
    assert list(origin["lon"]) == [MADRID_ORIGIN['lon']]
    assert list(origin["customdata"]) == ['madrid-origin']
    assert 'not a ranked destination' in origin["hovertext"][0]
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
    assert toledo["hover"].startswith(
        "<b>Toledo</b><br>Activities: History and heritage, Food and "
        "gastronomy<br>Average daytime temperature: 20.0 °C"
        "<br>Destination rank: 1 of 3<br>Destination score: 99.0/100"
    )
    assert "Destination rank: 3 of 3" in points["ES-41091"]["hover"]
    assert "Destination score: 65.4/100" in points["ES-40194"]["hover"]
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
    ranked, grey, origin = figure.to_plotly_json()["data"]
    assert list(ranked["customdata"]) == ["ES-45168", "ES-40194", "ES-41091"]
    assert list(ranked["marker"]["color"]) == pytest.approx(
        [100 - 61 / 60, 200 / 3 - 75 / 60, 200 / 3 - 5]
    )
    assert len(ranked["lat"]) + len(grey["lat"]) == 83
    assert grey["name"] == "No destination rank"


def test_map_keeps_all_catalogue_markers_fully_visible():
    points = map_points(CATALOG_ROWS)
    figure = map_figure(points)
    grey = figure.to_plotly_json()["data"][1]
    assert set(grey["customdata"]) == {row["city_id"] for row in CATALOG_ROWS}
    assert grey["marker"]["opacity"] == 0.95


# --------------------------------------------------------------- charts


# ------------------------------------------------- Dashboard page (83 cities)


HOT = {"ES-08019", "ES-41091", "ES-29067"}  # Barcelona, Seville, Málaga


def varied_handler(clock, failures=None):
    """Synthetic forecasts; HOT cities are 5 °C warmer than the rest."""
    base = catalog_handler(clock, failures=failures)
    by_coordinates = {(d.latitude, d.longitude): d for d in CATALOG.values()}

    def handle(url, params):
        response = base(url, params)
        if url.endswith("/forecast") and response.status_code == 200:
            assert isinstance(response._payload, dict)
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
    # Reserve the load for each test's configured scenario.
    app.session_state.dashboard_attempted_days = 3
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
    for trace in geo["data"][:2]:
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


def test_page_shows_map_and_criteria_after_reserved_load(page):
    app, _, session, _, factory = page
    markers = _markers(app)
    assert len(markers) == 83
    for place in CATALOG_ROWS:
        name, _, lat, lon = markers[place["city_id"]]
        assert name == "Weather not loaded"
        assert (lat, lon) == (place["latitude"], place["longitude"])
    assert app.selectbox(key="dashboard_days").value == 3
    assert app.button(key="dashboard_load").label == (
        "Refresh weather overview"
    )
    captions = _texts(app.caption)
    assert "16\u201324 \xb0C" in captions
    assert "follows each forecast" in captions
    assert "All 83 destinations are shown without weather" in _texts(
        app.info
    )
    assert len(_specs(app)) == 1  # the map only
    # Page scrolling over the map must not zoom it away from Spain.
    map_config = json.loads(app.get("plotly_chart")[0].proto.config)
    assert map_config["scrollZoom"] is False
    assert not session.calls and not factory.called
    assert "search_analysis_rows" not in app.session_state


def test_load_ranks_all_destinations_by_destination_score(page):
    app, service, session, _, factory = page
    _load(app)
    assert len(session.calls) == 83 and factory.call_count == 1
    assert len(service.store.load()) == 83 * 40  # every response saved
    overview = app.session_state["dashboard_overview"]
    rows = {r["city_id"]: r for r in overview["rows"]}
    assert len(rows) == 83
    assert "83 of 83 destinations can be ranked" in _texts(app.markdown)
    markers = _markers(app)
    assert {name for name, *_ in markers.values()} == {"Destination score"}
    ranks = destination_ranks(overview["rows"])
    assert ranks == {city: 1 + sum(
        other['final_score'] > row['final_score'] for other in rows.values())
        for city, row in rows.items()}
    for city, (_, hover, _, _) in markers.items():
        row = rows[city]
        temperature = f"{row['mean_temperature_c']:.1f} °C"
        assert f"Average daytime temperature: {temperature}" in hover
        assert f"Destination rank: {ranks[city]} of 83" in hover
        assert f"Destination score: {row['final_score']:.1f}/100" in hover
    full = next(d.value for d in app.dataframe
                if "Driving distance (km)" in d.value.columns)
    assert full["Destination score / 100"].tolist() == pytest.approx(
        [rows[CATALOG_BY_NAME[name]]["final_score"]
         for name in full["Destination"]])
    assert full["Destination score / 100"].is_monotonic_decreasing
    assert len(_specs(app)) == 2  # map and executive scatter


@pytest.mark.parametrize("days", [1, 2, 3, 4, 5])
def test_each_window_covers_three_slots_per_day(page, days):
    app, _, session, _, _ = page
    app.selectbox(key="dashboard_days").set_value(days).run()
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
        app.selectbox(key="dashboard_days").set_value(days).run()
        _load(app)
    assert len(session.calls) == 83
    assert service.store.path.read_bytes() == saved
    assert app.session_state["dashboard_overview"]["cached"] == 83


def test_navigation_and_windows_make_no_requests(page):
    app, service, session, _, _ = page
    _load(app)
    saved = service.store.path.read_bytes()
    before = app.session_state["dashboard_overview"]
    assert not app.multiselect
    assert len(_markers(app)) == 83
    app.selectbox(key="dashboard_days").set_value(5).run()
    app.sidebar.radio[0].set_value("Searcher").run()
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert not app.exception and not app.multiselect
    assert app.selectbox(key="dashboard_days").value == 5
    assert app.session_state["dashboard_overview"] != before
    assert app.session_state["dashboard_overview"]["preferences"].days == 5
    assert "Your settings have changed" not in _texts(app.info)
    assert "next 5 day(s)" in _texts(app.caption)
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
    for row in search_rows:  # Same saved weather, different scoring modes
        assert row["weather_match_pct"] != (
            by_city[row["city_id"]]["weather_match_pct"]
        )
    app.sidebar.radio[0].set_value("Dashboard").run()
    assert app.session_state["dashboard_overview"]["rows"] == dashboard_rows
    assert not app.multiselect
    assert len(_markers(app)) == 83


def test_partial_failure_keeps_every_marker_with_neutral_reason(page):
    app, _, session, clock, _ = page
    session.handler = varied_handler(clock, failures={SEGOVIA.city_id: 404})
    _load(app)
    assert "82 of 83 destinations can be ranked" in _texts(app.markdown)
    name, hover, _, _ = _markers(app)[SEGOVIA.city_id]
    assert name == "No destination rank"
    assert searcher.MESSAGES["location_not_found"] in hover
    assert "°C" not in hover and "Destination rank" not in hover
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
    assert "local storage failed" in _texts(app.error)
    assert "82 remaining destinations were not requested" in _texts(
        app.caption
    )
    assert "40 fetched weather records" in _texts(app.warning)
    monkeypatch.setattr(service.store, "append", real_append)
    _load(app)
    assert service.unsaved_record_count == 0
    assert "83 of 83" in _texts(app.markdown)
    # Recover the kept response before any new HTTP; reuse it for ranking.
    assert len(session.calls) == 83
    assert len(service.store.load()) == 83 * 40
    assert "local storage failed" not in _texts(app.error)


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
    assert "22–30 °C" in _texts(app.caption)
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
    fetched = {c["params"]["id"] for c in session.calls}
    for place in (TOLEDO, SEGOVIA, SEVILLE):  # reused genuine records
        assert service.client.request_parameters(place)["id"] not in fetched
    rows = {
        r["city_id"]: r
        for r in app.session_state["dashboard_overview"]["rows"]
    }
    expected = _independent_tally(header=header, rows=_genuine_lines(
        clock.now)[1], until=clock.now)
    for place in (SEVILLE, TOLEDO, SEGOVIA):
        assert rows[place.city_id]["weather_match_pct"] == pytest.approx(
            expected[place.city_id][0])
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
             float(by_time[t][col["wind_kmh"]]),
             float(by_time[t][col["cloud_pct"]]))
            for t in slots
        ]
        result[city] = (
            reference_score(values),
            sum(v[0] for v in values) / len(values),
        )
    return result


def test_genuine_82_destination_snapshot_matches_independent_tally(page):
    # Replay genuine history with today's mapping. Old provider identities
    # must refresh, not be relabeled. Failed fake requests ensure no synthetic
    # weather enters the independent numerical comparison.
    app, service, session, clock, _ = page
    clock.now = SNAPSHOT
    session.handler = lambda url, params: FakeResponse(404)
    header, rows = _genuine_lines(SNAPSHOT)
    mapping = load_location_overrides()
    latest = {}
    for values in rows:
        raw = dict(zip(header, values))
        if raw["kind"] != "forecast":
            continue
        city = raw["city_id"]
        stamp = datetime.fromisoformat(raw["retrieved_at_utc"])
        if city not in latest or stamp > latest[city][0]:
            latest[city] = (stamp, int(raw["provider_city_id"]))
    accepted = {city for city, (_, provider) in latest.items()
                if provider == mapping[city]["expected_provider_id"]}
    rejected = set(mapping) - accepted
    assert accepted and set(latest) - accepted  # exercise real changed IDs
    _write_csv(service.store.path, header, rows)
    before = service.store.path.read_bytes()
    _load(app, timeout=LARGE_STORE_TIMEOUT)

    assert {c["params"]["id"] for c in session.calls} == {
        mapping[city]["expected_provider_id"] for city in rejected}
    assert len(session.calls) == len(rejected)
    assert service.store.path.read_bytes() == before
    assert f"{len(accepted)} of 83 destinations can be ranked" in _texts(
        app.markdown)

    expected = _independent_tally(rows, header, SNAPSHOT)
    assert len(expected) == 82 and BARCELONA not in expected
    expected = {city: values for city, values in expected.items()
                if city in accepted}
    final = {c: max(0, score - min(CATALOG[c].car_duration_min / 30, 15))
             for c, (score, _) in expected.items()}
    want_rank = {c: 1 + sum(other > score for other in final.values())
                 for c, score in final.items()}
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
        assert name == "Destination score"
        assert f"Average daytime temperature: {mean_t:.1f} °C" in hover
        assert (f"Destination rank: {want_rank[city]} of {len(accepted)}"
                in hover)
        assert f"Destination score: {final[city]:.1f}/100" in hover
    for city in rejected:
        assert got[city]["status"] == "unavailable"
        assert got[city]["final_score"] is None
        name, hover, _, _ = markers[city]
        assert name == "No destination rank" and "°C" not in hover

    # The complete table retains verified destination rank and score order.
    order = sorted(expected, key=lambda c: (want_rank[c], c))
    names = {r["city_id"]: r["city"] for r in CATALOG_ROWS}
    full = next(d.value for d in app.dataframe
                if "Driving distance (km)" in d.value.columns)
    ranked = full[full["Status"] == "available"]
    assert ranked["Destination"].tolist() == [names[c] for c in order]
    assert ranked["Destination score / 100"].tolist() == pytest.approx(
        [final[c] for c in order])


def test_executive_scatter_agrees_with_catalogue_and_tabs_are_removed(page):
    app, _, _, _, _ = page
    _load(app)
    assert not app.tabs
    assert "Weather comparison and all preferences met" not in [
        expander.label for expander in app.expander]
    _, scatter = _specs(app)
    full = next(d.value for d in app.dataframe
                if "Driving distance (km)" in d.value.columns)
    assert scatter["data"][0]["y"] == pytest.approx(
        full["Destination score / 100"].tolist())
    assert scatter["data"][0]["x"] == pytest.approx([
        CATALOG[CATALOG_BY_NAME[name]].car_duration_min / 60
        for name in full["Destination"]])
    assert 'hours' in scatter['layout']['xaxis']['title']['text']
    assert '100' in scatter['layout']['yaxis']['title']['text']


def test_partial_data_never_removes_catalog_destinations(page):
    app, _, session, clock, _ = page
    session.handler = varied_handler(clock, failures={SEGOVIA.city_id: 404})
    _load(app)
    assert not app.multiselect
    assert len(_markers(app)) == 83
    assert app.dataframe[-1].value["Destination"].tolist() == ["Segovia"]
    full = next(d.value for d in app.dataframe
                if "Driving distance (km)" in d.value.columns)
    assert len(full) == 83
    assert set(full['Forecast']) == {'Next 3 day(s)'}
    assert {'Maximum rain probability (%)', 'Maximum wind (km/h)',
            'Activities', 'Driving time (h:mm)',
            'Retrieved (Madrid)', 'Age (h:mm)', 'Freshness',
            'Window starts (Madrid)', 'Window ends (Madrid)'} <= set(full)
    missing = full[full['Destination'] == 'Segovia'].iloc[0]
    assert full.loc[full['Destination'] == 'Segovia',
                    'Destination score / 100'].isna().all()
    assert missing['Unavailable reason']
    assert missing['Freshness'] == 'Unavailable'
    assert len(session.calls) == 83


def test_window_changes_recover_service_after_code_reload(page):
    from types import SimpleNamespace

    app, service, session, _, factory = page
    _load(app)
    saved = service.store.path.read_bytes()
    # A previous Python class survives in the session after a code update.
    app.session_state.weather_service = SimpleNamespace(unsaved_record_count=0)
    factory.reset_mock()
    for days in (2, 1, 3, 4, 5, 2):
        app.selectbox(key="dashboard_days").set_value(days).run()
        assert not app.exception and not app.error
        overview = app.session_state.dashboard_overview
        assert overview["preferences"].days == days
        assert len(overview["rows"]) == 83
        assert len(overview["daily"]) == 83 * days
        assert all(r["expected_periods"] == 3 * days
                   for r in overview["rows"])
        assert overview["cached"] == 83
        assert "not been refreshed" not in _texts(app.info)
    factory.assert_called_once()
    assert len(session.calls) == 83
    assert service.store.path.read_bytes() == saved
