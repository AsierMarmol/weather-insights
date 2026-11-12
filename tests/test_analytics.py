"""Offline tests for the P3.3 analytical engine.

Weather values here are synthetic test inputs, never genuine weather history;
nothing is written to data/weather. Destinations are the unchanged real catalog
rows. Expected answers are written out by hand from PHASE2_SCOPE.md rather
than recomputed with the engine's own formulas.
"""

from __future__ import annotations

import socket
from datetime import datetime, timedelta, timezone

import pytest

from weather_app.analytics import (
    RESULT_FIELDS,
    analyse_destinations,
    expected_period_times,
    is_daytime,
    is_eligible,
    ranking_key,
)
from weather_app.models import SearchPreferences, WeatherRecord
from weather_app.storage import load_destinations

UTC = timezone.utc
RUN_AT = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
DAY_PERIODS = [datetime(2026, 11, 12, h, tzinfo=UTC) for h in (9, 12, 15)]

TOLEDO, SEGOVIA, SEVILLE = "ES-45168", "ES-40194", "ES-41091"
FETCH = {
    SEVILLE: "00000000-0000-4000-8000-000000000001",
    TOLEDO: "00000000-0000-4000-8000-000000000002",
    SEGOVIA: "00000000-0000-4000-8000-000000000003",
}
# (temperature C, precipitation probability %, wind km/h) for 09/12/15 UTC.
WORKED = {
    TOLEDO: [(16, 30, 25), (20, 0, 10), (24, 30, 25)],
    SEGOVIA: [(25, 20, 20), (20, 31, 20), (20, 20, 26)],
    SEVILLE: [(16, 0, 0), (24, 30, 25), (25, 31, 26)],
}


@pytest.fixture(scope="module")
def catalog():
    return {d.city_id: d for d in load_destinations()}


@pytest.fixture
def three(catalog):
    return [catalog[SEVILLE], catalog[TOLEDO], catalog[SEGOVIA]]


def prefs(**overrides):
    values = dict(
        days=1,
        temperature_min_c=16,
        temperature_max_c=24,
        max_precipitation_probability_pct=30,
        max_wind_kmh=25,
    )
    values.update(overrides)
    return SearchPreferences(**values)


def record(
    city_id,
    valid_at,
    temp,
    pop,
    wind,
    *,
    fetch_id=None,
    retrieved=RUN_AT,
    kind="forecast",
):
    return WeatherRecord(
        fetch_id=fetch_id
        or FETCH.get(city_id, "00000000-0000-4000-8000-0000000000ff"),
        city_id=city_id,
        kind=kind,
        retrieved_at_utc=retrieved,
        valid_at_utc=valid_at,
        latitude=40.0,
        longitude=-4.0,
        temperature_c=temp,
        wind_kmh=wind,
        precipitation_probability_pct=pop,
        humidity_pct=60,
        cloud_pct=15,
        provider_city_id=1,
        provider_city_name="Synthetic",
    )


def group(city_id, values, times=DAY_PERIODS, **kwargs):
    return [record(city_id, t, *v, **kwargs) for t, v in zip(times, values)]


def worked_forecasts():
    return {city: group(city, values) for city, values in WORKED.items()}


def by_city(rows):
    return {row["city_id"]: row for row in rows}


# --- worked example and the three analyses


def test_worked_example_ranking_and_values(three):
    rows = analyse_destinations(three, worked_forecasts(), prefs(), RUN_AT)

    assert [r["city_id"] for r in rows] == [TOLEDO, SEGOVIA, SEVILLE]
    assert all(tuple(r) == RESULT_FIELDS for r in rows)
    toledo, segovia, seville = rows

    assert toledo["status"] == "available" and toledo["reason"] is None
    assert (
        toledo["temperature_passes"],
        toledo["precipitation_passes"],
        toledo["wind_passes"],
    ) == (3, 3, 3)
    assert toledo["weather_match_pct"] == 100
    assert toledo["travel_penalty"] == pytest.approx(61 / 60)
    assert toledo["final_score"] == pytest.approx(5939 / 60)
    assert (
        toledo["suitable_period_count"] == 3
        and toledo["all_preferences_pct"] == 100
    )

    assert segovia["weather_match_pct"] == pytest.approx(200 / 3)
    assert segovia["final_score"] == pytest.approx(785 / 12)
    assert (
        segovia["suitable_period_count"] == 0
        and segovia["all_preferences_pct"] == 0
    )

    assert seville["travel_penalty"] == 5  # 351 minutes capped at five
    assert seville["final_score"] == pytest.approx(185 / 3)
    assert seville["all_preferences_pct"] == pytest.approx(200 / 3)

    for row in rows:
        assert row["expected_periods"] == row["evaluated_periods"] == 3
        assert row["run_at_utc"] == "2026-11-11T18:30:00+00:00"
        assert row["forecast_retrieved_at_utc"] == "2026-11-11T18:30:00+00:00"
        assert row["days"] == 1


def test_weather_comparison_statistics(three):
    rows = by_city(
        analyse_destinations(three, worked_forecasts(), prefs(), RUN_AT)
    )
    assert rows[TOLEDO]["mean_temperature_c"] == pytest.approx(20)
    assert rows[TOLEDO]["max_precipitation_probability_pct"] == 30
    assert rows[TOLEDO]["max_wind_kmh"] == 25
    assert rows[SEGOVIA]["mean_temperature_c"] == pytest.approx(65 / 3)
    assert rows[SEGOVIA]["max_precipitation_probability_pct"] == 31
    assert rows[SEGOVIA]["max_wind_kmh"] == 26


def test_same_weather_match_different_simultaneous_suitability(three):
    rows = by_city(
        analyse_destinations(three, worked_forecasts(), prefs(), RUN_AT)
    )
    assert (
        rows[SEGOVIA]["weather_match_pct"]
        == rows[SEVILLE]["weather_match_pct"]
    )
    assert rows[SEGOVIA]["all_preferences_pct"] == 0
    assert rows[SEVILLE]["all_preferences_pct"] == pytest.approx(200 / 3)


def test_bounds_are_inclusive_and_just_outside_fails(catalog):
    toledo = catalog[TOLEDO]
    edge = {TOLEDO: group(TOLEDO, [(16, 30, 25), (24, 30, 25), (24, 30, 25)])}
    assert (
        analyse_destinations([toledo], edge, prefs(), RUN_AT)[0][
            "weather_match_pct"
        ]
        == 100
    )

    outside = {TOLEDO: group(TOLEDO, [(15.9, 30.1, 25.1)] * 3)}
    row = analyse_destinations([toledo], outside, prefs(), RUN_AT)[0]
    assert row["status"] == "available"  # imperfect weather stays eligible
    # floored, not negative
    assert row["weather_match_pct"] == 0 and row["final_score"] == 0
    assert row["suitable_period_count"] == 0


def test_records_outside_window_or_at_night_are_ignored(catalog):
    toledo = catalog[TOLEDO]
    extra_times = [
        datetime(2026, 11, 11, 18, tzinfo=UTC),  # before run_at
        datetime(2026, 11, 12, 6, tzinfo=UTC),  # 07:00 Madrid, before daytime
        datetime(2026, 11, 12, 18, tzinfo=UTC),  # 19:00 Madrid, after daytime
        datetime(2026, 11, 13, 12, tzinfo=UTC),  # beyond the one-day window
    ]
    records = group(TOLEDO, WORKED[TOLEDO]) + [
        record(TOLEDO, t, 40, 100, 90) for t in extra_times
    ]
    row = analyse_destinations([toledo], {TOLEDO: records}, prefs(), RUN_AT)[0]
    assert row["evaluated_periods"] == 3 and row["weather_match_pct"] == 100
    assert row["max_wind_kmh"] == 25


# --- time window and daytime coverage


def test_expected_periods_for_one_and_five_days():
    assert expected_period_times(RUN_AT, 1) == DAY_PERIODS
    five = expected_period_times(RUN_AT, 5)
    assert len(five) == 15
    assert five[-1] == datetime(2026, 11, 16, 15, tzinfo=UTC)


def test_window_excludes_run_at_and_includes_end():
    run_at = datetime(2026, 11, 12, 9, tzinfo=UTC)
    assert expected_period_times(run_at, 1) == [
        datetime(2026, 11, 12, 12, tzinfo=UTC),
        datetime(2026, 11, 12, 15, tzinfo=UTC),
        datetime(2026, 11, 13, 9, tzinfo=UTC),
    ]


def test_daytime_follows_madrid_clock_change():
    # Clocks go back on 25 October 2026 (CEST UTC+2 -> CET UTC+1).
    run_at = datetime(2026, 10, 24, 12, tzinfo=UTC)
    assert expected_period_times(run_at, 2) == [
        datetime(2026, 10, 24, 15, tzinfo=UTC),  # 17:00 CEST
        datetime(2026, 10, 25, 9, tzinfo=UTC),  # 10:00 CET
        datetime(2026, 10, 25, 12, tzinfo=UTC),
        datetime(2026, 10, 25, 15, tzinfo=UTC),  # 16:00 CET
        datetime(2026, 10, 26, 9, tzinfo=UTC),
        # window ends 12:00 UTC inclusive
        datetime(2026, 10, 26, 12, tzinfo=UTC),
    ]
    # Summer: 06:00 UTC is 08:00 CEST (excluded), 15:00 UTC is 17:00 CEST
    # (included).
    summer = expected_period_times(datetime(2026, 7, 1, 0, 30, tzinfo=UTC), 1)
    assert summer == [datetime(2026, 7, 1, h, tzinfo=UTC) for h in (9, 12, 15)]


def test_daytime_boundaries_in_local_time():
    # 08:00 UTC is 09:00 CET (included); 17:00 UTC is 18:00 CET (excluded).
    assert is_daytime(datetime(2026, 11, 12, 8, tzinfo=UTC))
    assert not is_daytime(datetime(2026, 11, 12, 7, 59, 59, tzinfo=UTC))
    assert is_daytime(datetime(2026, 11, 12, 16, 59, 59, tzinfo=UTC))
    assert not is_daytime(datetime(2026, 11, 12, 17, tzinfo=UTC))
    # Summer (CEST): 07:00 UTC is 09:00 local, 16:00 UTC is 18:00 local.
    assert is_daytime(datetime(2026, 7, 1, 7, tzinfo=UTC))
    assert not is_daytime(datetime(2026, 7, 1, 16, tzinfo=UTC))


def test_missing_fifth_day_period_is_unavailable(catalog):
    toledo = catalog[TOLEDO]
    times = expected_period_times(RUN_AT, 5)
    complete = [record(TOLEDO, t, 20, 0, 10) for t in times]
    assert (
        analyse_destinations(
            [toledo], {TOLEDO: complete}, prefs(days=5), RUN_AT
        )[0]["evaluated_periods"]
        == 15
    )

    dropped = [
        r
        for r in complete
        if r.valid_at_utc != datetime(2026, 11, 16, 12, tzinfo=UTC)
    ]
    row = analyse_destinations(
        [toledo], {TOLEDO: dropped}, prefs(days=5), RUN_AT
    )[0]
    assert (row["status"], row["reason"]) == ("unavailable", "missing_periods")
    assert row["expected_periods"] == 15 and row["evaluated_periods"] == 0


# --- unavailable states and precedence


def test_unavailable_row_shape(three):
    forecasts = worked_forecasts()
    forecasts[TOLEDO] = [
        r for r in forecasts[TOLEDO] if r.valid_at_utc != DAY_PERIODS[1]
    ]
    rows = analyse_destinations(three, forecasts, prefs(), RUN_AT)
    assert [r["city_id"] for r in rows] == [SEGOVIA, SEVILLE, TOLEDO]
    toledo = rows[-1]
    assert (toledo["status"], toledo["reason"]) == (
        "unavailable",
        "missing_periods",
    )
    assert toledo["expected_periods"] == 3 and toledo["evaluated_periods"] == 0
    assert toledo["forecast_retrieved_at_utc"] == "2026-11-11T18:30:00+00:00"
    for name in RESULT_FIELDS[8:]:
        assert toledo[name] is None, name


def test_missing_probability_is_missing_metrics(catalog):
    records = group(TOLEDO, [(16, None, 25), (20, 0, 10), (24, 30, 25)])
    row = analyse_destinations(
        [catalog[TOLEDO]], {TOLEDO: records}, prefs(), RUN_AT
    )[0]
    assert row["reason"] == "missing_metrics" and row["final_score"] is None


def test_no_forecast_is_fetch_failed(three):
    rows = analyse_destinations(three, {TOLEDO: []}, prefs(), RUN_AT)
    assert [(r["city_id"], r["reason"]) for r in rows] == [
        (SEGOVIA, "fetch_failed"),
        (SEVILLE, "fetch_failed"),
        (TOLEDO, "fetch_failed"),
    ]
    assert all(r["forecast_retrieved_at_utc"] is None for r in rows)


def test_staleness_boundary(catalog):
    toledo = catalog[TOLEDO]

    def reason(retrieved):
        records = group(TOLEDO, WORKED[TOLEDO], retrieved=retrieved)
        return analyse_destinations(
            [toledo], {TOLEDO: records}, prefs(), RUN_AT
        )[0]["reason"]

    assert reason(datetime(2026, 11, 11, 14, tzinfo=UTC)) == "stale_forecast"
    assert reason(RUN_AT - timedelta(hours=3)) is None  # equality is allowed
    assert reason(RUN_AT - timedelta(hours=3, seconds=1)) == "stale_forecast"
    # batch receipt after run_at
    assert reason(RUN_AT + timedelta(minutes=2)) is None


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda rs: [
                record(SEGOVIA, r.valid_at_utc, 20, 0, 10) for r in rs
            ],
            id="other-city",
        ),
        pytest.param(
            lambda rs: rs[:2]
            + [
                record(
                    TOLEDO,
                    DAY_PERIODS[2],
                    20,
                    0,
                    10,
                    fetch_id="00000000-0000-4000-8000-0000000000aa",
                )
            ],
            id="mixed-fetch",
        ),
        pytest.param(
            lambda rs: rs[:2]
            + [
                record(
                    TOLEDO,
                    DAY_PERIODS[2],
                    20,
                    0,
                    10,
                    retrieved=RUN_AT - timedelta(minutes=1),
                )
            ],
            id="mixed-retrieval",
        ),
        pytest.param(
            lambda rs: [
                record(TOLEDO, r.valid_at_utc, 20, None, 10, kind="current")
                for r in rs
            ],
            id="current-kind",
        ),
    ],
)
def test_identity_and_mixed_groups_are_invalid_data(catalog, mutate):
    records = mutate(group(TOLEDO, WORKED[TOLEDO]))
    row = analyse_destinations(
        [catalog[TOLEDO]], {TOLEDO: records}, prefs(), RUN_AT
    )[0]
    assert row["reason"] == "invalid_data"
    assert row["forecast_retrieved_at_utc"] is None


def test_duplicate_valid_time_is_duplicate_periods(catalog):
    records = group(TOLEDO, WORKED[TOLEDO]) + [
        record(TOLEDO, DAY_PERIODS[0], 18, 0, 10)
    ]
    row = analyse_destinations(
        [catalog[TOLEDO]], {TOLEDO: records}, prefs(), RUN_AT
    )[0]
    assert row["reason"] == "duplicate_periods"


def test_reason_precedence(catalog):
    toledo = catalog[TOLEDO]
    stale = RUN_AT - timedelta(hours=5)
    # Stale beats duplicate, missing period and missing metric.
    records = [
        record(TOLEDO, DAY_PERIODS[0], 20, None, 10, retrieved=stale),
        record(TOLEDO, DAY_PERIODS[0], 20, None, 10, retrieved=stale),
    ]
    assert (
        analyse_destinations([toledo], {TOLEDO: records}, prefs(), RUN_AT)[0][
            "reason"
        ]
        == "stale_forecast"
    )
    # Duplicate beats missing period and missing metric.
    records = [record(TOLEDO, DAY_PERIODS[0], 20, None, 10)] * 2
    assert (
        analyse_destinations([toledo], {TOLEDO: records}, prefs(), RUN_AT)[0][
            "reason"
        ]
        == "duplicate_periods"
    )
    # Missing period beats missing metric.
    records = [record(TOLEDO, DAY_PERIODS[0], 20, None, 10)]
    assert (
        analyse_destinations([toledo], {TOLEDO: records}, prefs(), RUN_AT)[0][
            "reason"
        ]
        == "missing_periods"
    )


# --- filters, ordering and inputs


def test_activity_filter_matches_any(three):
    rows = analyse_destinations(
        three,
        worked_forecasts(),
        prefs(activities=("History and heritage", "Coast")),
        RUN_AT,
    )
    assert [r["city_id"] for r in rows] == [TOLEDO, SEVILLE]


def test_size_filter_and_groups_combine_with_and(three):
    small = prefs(destination_sizes=("Small city or town",))
    assert [
        r["city_id"]
        for r in analyse_destinations(three, worked_forecasts(), small, RUN_AT)
    ] == [
        TOLEDO,
        SEGOVIA,
    ]
    both = prefs(
        destination_sizes=("Small city or town",),
        activities=("History and heritage",),
    )
    assert [
        r["city_id"]
        for r in analyse_destinations(three, worked_forecasts(), both, RUN_AT)
    ] == [TOLEDO]


def test_filters_on_full_catalog(catalog):
    destinations = list(catalog.values())
    assert (
        len(analyse_destinations(destinations, {}, prefs(days=3), RUN_AT))
        == 83
    )
    counts = {
        size: sum(
            is_eligible(d, prefs(destination_sizes=(size,)))
            for d in destinations
        )
        for size in ("Large city", "Medium city", "Small city or town")
    }
    assert counts == {
        "Large city": 14,
        "Medium city": 26,
        "Small city or town": 43,
    }


def test_tie_breaking_order():
    rows = [
        {
            "city_id": "ES-45168",
            "final_score": 95.0,
            "weather_match_pct": 100.0,
        },
        {
            "city_id": "ES-41091",
            "final_score": 95.0,
            "weather_match_pct": 100.0,
        },
        {
            "city_id": "ES-40194",
            "final_score": 95.0,
            "weather_match_pct": 100.0,
        },
        {
            "city_id": "ES-08019",
            "final_score": 97.0,
            "weather_match_pct": 100.0,
        },
        {
            "city_id": "ES-28079",
            "final_score": 95.0,
            "weather_match_pct": 99.0,
        },
    ]
    minutes = {
        "ES-45168": 300,
        "ES-41091": 360,
        "ES-40194": 300,
        "ES-08019": 180,
        "ES-28079": 10,
    }
    ordered = sorted(rows, key=lambda r: ranking_key(r, minutes[r["city_id"]]))
    assert [r["city_id"] for r in ordered] == [
        "ES-08019",
        "ES-40194",
        "ES-45168",
        "ES-41091",
        "ES-28079",
    ]


def test_engine_breaks_equal_scores_by_drive_then_city_id(catalog):
    # Seville (351 min) and Barcelona-like long drives are both capped at 5,
    # so identical weather gives identical scores; then minutes, then city_id.
    long_drives = sorted(
        (d for d in catalog.values() if d.car_duration_min >= 300),
        key=lambda d: d.city_id,
    )[:2]
    toledo = catalog[TOLEDO]
    chosen = long_drives + [toledo]
    forecasts = {
        d.city_id: group(d.city_id, [(20, 0, 10)] * 3, fetch_id=None)
        for d in chosen
    }
    rows = analyse_destinations(chosen, forecasts, prefs(), RUN_AT)
    long_sorted = sorted(
        long_drives, key=lambda d: (d.car_duration_min, d.city_id)
    )
    assert [r["city_id"] for r in rows] == [TOLEDO] + [
        d.city_id for d in long_sorted
    ]
    assert rows[1]["final_score"] == rows[2]["final_score"] == 95


@pytest.mark.parametrize(
    "run_at",
    [
        datetime(2026, 11, 11, 18, 30),
        datetime(2026, 11, 11, 19, 30, tzinfo=timezone(timedelta(hours=1))),
        "2026-11-11T18:30:00+00:00",
    ],
    ids=["naive", "non-utc-offset", "string"],
)
def test_rejects_invalid_run_time(three, run_at):
    with pytest.raises(ValueError, match="invalid_input"):
        analyse_destinations(three, worked_forecasts(), prefs(), run_at)


def test_rejects_invalid_preferences_and_inputs(three):
    with pytest.raises(ValueError):
        prefs(temperature_min_c=25, temperature_max_c=16)
    with pytest.raises(ValueError, match="invalid_input"):
        analyse_destinations(three, worked_forecasts(), {"days": 1}, RUN_AT)
    with pytest.raises(ValueError, match="invalid_input"):
        analyse_destinations(
            three + three[:1], worked_forecasts(), prefs(), RUN_AT
        )


def test_is_pure(three, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("analytics must not open network connections")

    monkeypatch.setattr(socket, "socket", no_network)
    forecasts = worked_forecasts()
    snapshot = {city: list(records) for city, records in forecasts.items()}
    first = analyse_destinations(three, forecasts, prefs(), RUN_AT)
    assert analyse_destinations(three, forecasts, prefs(), RUN_AT) == first
    assert forecasts == snapshot
