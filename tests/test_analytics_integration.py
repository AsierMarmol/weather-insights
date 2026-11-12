"""P3.3 integration: the analytics engine on the real P3.1/P3.2 components.

The service tests use fake HTTP with SYNTHETIC weather and a WeatherStore in a
temporary directory. The genuine-data test only reads the committed
data/weather/weather_records.csv; it never writes to it. Expected answers are
worked out by hand, not recomputed with the engine's formulas.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from weather_fakes import (
    CATALOG,
    SEGOVIA,
    TOLEDO,
    Clock,
    FakeSession,
    catalog_handler,
    make_client,
)

from weather_app.analytics import analyse_destinations, forecasts_from_service
from weather_app.models import SearchPreferences
from weather_app.service import WeatherService
from weather_app.storage import WEATHER_RECORDS_PATH, WeatherStore

UTC = timezone.utc
SEVILLE = CATALOG["ES-41091"]
# Synthetic forecasts start three hours after this, at 09:00 UTC, on the native
# grid.
NOW = datetime(2026, 11, 12, 6, 0, tzinfo=UTC)


def prefs(days=1, **overrides):
    values = dict(
        days=days,
        temperature_min_c=16,
        temperature_max_c=24,
        max_precipitation_probability_pct=30,
        max_wind_kmh=25,
    )
    values.update(overrides)
    return SearchPreferences(**values)


@pytest.fixture
def service(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(
        handler=catalog_handler(clock, failures={SEVILLE.city_id: 404})
    )
    store = WeatherStore(tmp_path / "weather_records.csv")
    return (
        WeatherService(make_client(session, clock), store, clock=clock),
        session,
        store,
    )


def test_service_results_feed_the_engine(service):
    weather, session, store = service
    destinations = [SEVILLE, TOLEDO, SEGOVIA]
    results = weather.forecast_many(destinations)
    rows = analyse_destinations(
        destinations, forecasts_from_service(results), prefs(), NOW
    )

    # Synthetic periods 09/12/15 UTC: 18/19/20 C, pop 0.3 -> 30 %, wind 3 m/s
    # -> 10.8 km/h.
    # Every check passes, so the ranking is decided by driving time alone.
    assert [(r["city_id"], r["status"], r["reason"]) for r in rows] == [
        (TOLEDO.city_id, "available", None),
        (SEGOVIA.city_id, "available", None),
        (SEVILLE.city_id, "unavailable", "fetch_failed"),
    ]
    toledo, segovia, seville = rows
    assert (
        toledo["weather_match_pct"] == 100
        and toledo["all_preferences_pct"] == 100
    )
    assert toledo["final_score"] == pytest.approx(100 - 61 / 60)
    assert segovia["final_score"] == pytest.approx(100 - 75 / 60)
    assert toledo["mean_temperature_c"] == pytest.approx(19)
    assert toledo["max_precipitation_probability_pct"] == 30
    assert toledo["max_wind_kmh"] == pytest.approx(10.8)
    assert toledo["forecast_retrieved_at_utc"] == NOW.isoformat()
    assert seville["forecast_retrieved_at_utc"] is None
    assert results[SEVILLE.city_id]["error"]["code"] == "location_not_found"

    # A rerun reuses the cached forecasts: only the failed city is requested
    # again,
    # no rows are added and the analysis is identical.
    assert (len(session.calls), len(store.load())) == (3, 80)
    again = analyse_destinations(
        destinations,
        forecasts_from_service(weather.forecast_many(destinations)),
        prefs(),
        NOW,
    )
    assert again == rows
    assert (len(session.calls), len(store.load())) == (4, 80)
    assert session.calls[-1]["params"]["lat"] == SEVILLE.latitude


def test_saved_records_reload_into_the_same_analysis(service):
    weather, _, store = service
    results = weather.forecast_many([TOLEDO, SEGOVIA])
    reloaded = {city: store.latest_forecast(city) for city in results}
    for days in (1, 3, 5):
        from_service = analyse_destinations(
            [TOLEDO, SEGOVIA],
            forecasts_from_service(results),
            prefs(days),
            NOW,
        )
        from_store = analyse_destinations(
            [TOLEDO, SEGOVIA], reloaded, prefs(days), NOW
        )
        assert from_service == from_store
    # Forty periods from 09:00 UTC cover all fifteen daytime periods of five
    # days.
    assert from_store[0]["evaluated_periods"] == 15


def test_adapter_rejects_malformed_results():
    with pytest.raises(ValueError, match="invalid_input"):
        forecasts_from_service([])
    with pytest.raises(ValueError, match="invalid_input"):
        forecasts_from_service({"ES-45168": {"records": []}})


# --- genuine saved data

# P3.2 live check, 12 Nov 2026
GENUINE_TOLEDO_FETCH = "4e96b491-da9f-4edd-8f14-f2f6726a5fd7"


@pytest.fixture(scope="module")
def genuine_toledo():
    before = WEATHER_RECORDS_PATH.read_bytes()
    records = [
        r
        for r in WeatherStore().load(city_id=TOLEDO.city_id, kind="forecast")
        if r.fetch_id == GENUINE_TOLEDO_FETCH
    ]
    yield records
    assert WEATHER_RECORDS_PATH.read_bytes() == before  # read-only


def test_genuine_toledo_forecast_one_day(genuine_toledo):
    assert len(genuine_toledo) == 40
    # replay at the original retrieval time
    run_at = genuine_toledo[0].retrieved_at_utc
    row = analyse_destinations(
        [TOLEDO], {TOLEDO.city_id: genuine_toledo}, prefs(), run_at
    )[0]

    # Hand check against the saved CSV rows inside (10:28 UTC 12 Nov, 10:28 UTC
    # 13 Nov]
    # and Madrid 09:00-18:00: 12 Nov 12:00 (16.54 C, 100 %, 28.512 km/h),
    # 12 Nov 15:00 (17.19 C, 39 %, 26.424 km/h), 13 Nov 09:00 (15.47 C, 88 %,
    # 17.928 km/h).
    assert row["status"] == "available"
    assert (row["expected_periods"], row["evaluated_periods"]) == (3, 3)
    assert (
        row["temperature_passes"],
        row["precipitation_passes"],
        row["wind_passes"],
    ) == (2, 0, 1)
    assert row["weather_match_pct"] == pytest.approx(100 / 3)
    assert row["final_score"] == pytest.approx(100 / 3 - 61 / 60)
    assert row["suitable_period_count"] == 0
    assert row["mean_temperature_c"] == pytest.approx(
        (16.54 + 17.19 + 15.47) / 3
    )
    assert row["max_precipitation_probability_pct"] == 100
    assert row["max_wind_kmh"] == pytest.approx(28.512)


def test_genuine_toledo_forecast_covers_five_days(genuine_toledo):
    run_at = genuine_toledo[0].retrieved_at_utc
    row = analyse_destinations(
        [TOLEDO], {TOLEDO.city_id: genuine_toledo}, prefs(5), run_at
    )[0]
    assert row["status"] == "available"
    assert row["expected_periods"] == row["evaluated_periods"] == 15
    # Four hours later the same forecast is stale and no longer recommended.
    later = run_at + timedelta(hours=4)
    stale = analyse_destinations(
        [TOLEDO], {TOLEDO.city_id: genuine_toledo}, prefs(5), later
    )[0]
    assert (stale["status"], stale["reason"]) == (
        "unavailable",
        "stale_forecast",
    )


# P2.5 genuine sample: fixed fetch IDs keep this replay stable as data
# accumulates.
P25_FORECASTS = {
    "ES-45168": "5f188094-18a9-471c-9155-81a82d6caae3",
    "ES-40194": "93c655ea-1a12-4b06-bb42-cda59497238c",
    "ES-41091": "9bb6a9d5-dd22-482d-ae30-85db8ed1b51b",
}


@pytest.mark.parametrize("days", [1, 2, 3, 4, 5])
def test_p25_genuine_multi_city_replay(days):
    before = WEATHER_RECORDS_PATH.read_bytes()
    records = WeatherStore().load()
    forecasts = {
        city: [r for r in records if r.fetch_id == fetch_id]
        for city, fetch_id in P25_FORECASTS.items()
    }
    assert all(len(group) == 40 for group in forecasts.values())
    run_at = datetime.fromisoformat("2026-11-12T11:29:04.669987+00:00")
    rows = analyse_destinations(
        [TOLEDO, SEGOVIA, SEVILLE], forecasts, prefs(days), run_at
    )
    assert all(r["status"] == "available" for r in rows)
    assert all(
        r["expected_periods"] == r["evaluated_periods"] == days * 3
        for r in rows
    )
    if days == 3:
        # Independent tally of nine daytime CSV periods: Seville 24/27,
        # Toledo 14/27, Segovia 13/27 checks, less each driving penalty.
        assert [r["city_id"] for r in rows] == [
            "ES-41091",
            "ES-45168",
            "ES-40194",
        ]
        assert [r["final_score"] for r in rows] == pytest.approx(
            [
                100 * 24 / 27 - 5,
                100 * 14 / 27 - 61 / 60,
                100 * 13 / 27 - 75 / 60,
            ]
        )
    assert WEATHER_RECORDS_PATH.read_bytes() == before
