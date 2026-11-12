"""P5.3 analytical acceptance: boundaries not already proven elsewhere.

Synthetic weather values are test inputs only. The genuine-data tests read
data/weather/weather_records.csv with the csv module, replay it at its
historical reference time and check that its bytes are unchanged. Expected
answers come from hand reasoning or from an independent tally of the raw CSV
rows (no WeatherRecord, zoneinfo or analytics code), never from the engine.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pytest

from weather_app.analytics import (
    analyse_destinations,
    expected_period_times,
)
from weather_app.config import load_product_defaults
from weather_app.dashboard import (
    filter_frame,
    overview_preferences,
    prepare_frame,
    weather_ranks,
)
from weather_app.models import SearchPreferences, WeatherRecord
from weather_app.storage import (
    WEATHER_RECORDS_PATH,
    WeatherStore,
    load_destinations,
)

UTC = timezone.utc
CATALOG = {d.city_id: d for d in load_destinations()}
CATALOG_ROWS = [d.as_catalog_row() for d in CATALOG.values()]
TOLEDO, SEGOVIA, SEVILLE = "ES-45168", "ES-40194", "ES-41091"
SYNTHETIC_FETCH = "00000000-0000-4000-8000-0000000000c3"


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


def record(city_id, valid_at, temp, pop, wind, *, retrieved, fetch_id=None):
    return WeatherRecord(
        fetch_id=fetch_id or SYNTHETIC_FETCH,
        city_id=city_id,
        kind="forecast",
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


def provider_group(city_id, retrieved, values=(20, 0, 10), periods=40):
    """Forty three-hour slots starting at the first grid time after
    retrieval, like the genuine responses (see the CSV replay below)."""
    first = retrieved.replace(minute=0, second=0, microsecond=0)
    first += timedelta(hours=3 - first.hour % 3)
    return [
        record(city_id, first + timedelta(hours=3 * i), *values,
               retrieved=retrieved, fetch_id=SYNTHETIC_FETCH)
        for i in range(periods)
    ]


# --- 1. windows, daytime, clock changes and date boundaries


def _reference_times():
    """Every 7 h 13 min 17 s over a full year: all hours, both clock
    changes, month and year ends, on and off the three-hour grid."""
    moment = datetime(2026, 3, 1, 0, 0, 1, tzinfo=UTC)
    while moment < datetime(2027, 4, 1, tzinfo=UTC):
        yield moment
        moment += timedelta(hours=7, minutes=13, seconds=17)


def test_every_window_has_three_daytime_slots_per_day_all_year():
    # Madrid is UTC+1 (CET) or UTC+2 (CEST), so the grid times inside
    # 09:00-18:00 local are always 09/12/15 UTC: 10/13/16 CET or
    # 11/14/17 CEST. Every 24 h window therefore holds exactly three
    # slots, and a five-day window never shrinks to fewer than fifteen.
    for run_at in _reference_times():
        for days in range(1, 6):
            times = expected_period_times(run_at, days)
            end = run_at + timedelta(hours=24 * days)
            assert len(times) == 3 * days, (run_at, days)
            assert all(run_at < t <= end for t in times)
            assert {t.hour for t in times} <= {9, 12, 15}
            assert all(t.minute == t.second == 0 for t in times)


def test_spring_clock_change_keeps_three_slots_each_day():
    # Clocks go forward on 28 March 2027 at 01:00 UTC (CET -> CEST).
    run_at = datetime(2027, 3, 27, 13, tzinfo=UTC)
    assert expected_period_times(run_at, 2) == [
        datetime(2027, 3, 27, 15, tzinfo=UTC),  # 16:00 CET
        datetime(2027, 3, 28, 9, tzinfo=UTC),  # 11:00 CEST
        datetime(2027, 3, 28, 12, tzinfo=UTC),
        datetime(2027, 3, 28, 15, tzinfo=UTC),  # 17:00 CEST
        datetime(2027, 3, 29, 9, tzinfo=UTC),
        datetime(2027, 3, 29, 12, tzinfo=UTC),  # end 13:00 UTC inclusive
    ]


@pytest.mark.parametrize("run_at", [
    # 23:30 UTC 31 Dec is already 00:30 on 1 January in Madrid.
    datetime(2026, 12, 31, 23, 30, tzinfo=UTC),
    # One second before local midnight.
    datetime(2026, 12, 31, 22, 59, 59, tzinfo=UTC),
])
def test_year_boundary_uses_the_utc_window_not_the_local_date(run_at):
    assert expected_period_times(run_at, 1) == [
        datetime(2027, 1, 1, h, tzinfo=UTC) for h in (9, 12, 15)
    ]


def test_fifth_day_end_slot_is_included_and_required():
    run_at = datetime(2026, 11, 12, 9, tzinfo=UTC)
    times = expected_period_times(run_at, 5)
    assert times[0] == datetime(2026, 11, 12, 12, tzinfo=UTC)  # not 09:00
    assert times[-1] == datetime(2026, 11, 17, 9, tzinfo=UTC)  # the end
    toledo = CATALOG[TOLEDO]
    full = [record(TOLEDO, t, 20, 0, 10, retrieved=run_at) for t in times]
    row = analyse_destinations([toledo], {TOLEDO: full}, prefs(5), run_at)[0]
    assert row["evaluated_periods"] == 15
    row = analyse_destinations(
        [toledo], {TOLEDO: full[:-1]}, prefs(5), run_at
    )[0]
    assert (row["reason"], row["evaluated_periods"]) == ("missing_periods", 0)


def test_cached_forecast_that_no_longer_reaches_day_five_is_unavailable():
    # Retrieved 10:28 -> provider slots 12 Nov 12:00 ... 17 Nov 09:00.
    retrieved = datetime(2026, 11, 12, 10, 28, tzinfo=UTC)
    records = provider_group(TOLEDO, retrieved)
    assert records[-1].valid_at_utc == datetime(2026, 11, 17, 9, tzinfo=UTC)
    toledo = CATALOG[TOLEDO]

    at_retrieval = analyse_destinations(
        [toledo], {TOLEDO: records}, prefs(5), retrieved
    )[0]
    assert at_retrieval["evaluated_periods"] == 15

    # Three hours later the group is still fresh (equality is allowed), but
    # the window now ends 17 Nov 13:28 and needs the 12:00 slot, which the
    # forecast does not contain: unavailable, never a 14-slot result.
    later = retrieved + timedelta(hours=3)
    row = analyse_destinations([toledo], {TOLEDO: records}, prefs(5), later)[0]
    assert (row["status"], row["reason"]) == ("unavailable", "missing_periods")
    assert row["weather_match_pct"] is None and row["final_score"] is None
    for days in range(1, 5):  # shorter windows are still fully covered
        assert analyse_destinations(
            [toledo], {TOLEDO: records}, prefs(days), later
        )[0]["evaluated_periods"] == 3 * days


# --- 2/6. missing metrics, malformed values and fetch groups


@pytest.mark.parametrize("missing", ["temperature", "probability", "wind"])
def test_any_missing_daytime_metric_is_unavailable_not_zero(missing):
    run_at = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
    values = {"temperature": (None, 0, 10), "probability": (20, None, 10),
              "wind": (20, 0, None)}[missing]
    times = expected_period_times(run_at, 1)
    records = [record(TOLEDO, times[0], *values, retrieved=run_at)] + [
        record(TOLEDO, t, 20, 0, 10, retrieved=run_at) for t in times[1:]
    ]
    row = analyse_destinations(
        [CATALOG[TOLEDO]], {TOLEDO: records}, prefs(), run_at
    )[0]
    assert (row["status"], row["reason"]) == ("unavailable", "missing_metrics")
    assert row["evaluated_periods"] == 0
    assert row["temperature_passes"] is None
    assert row["mean_temperature_c"] is None


def test_missing_values_outside_the_window_do_not_matter():
    run_at = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
    records = [
        record(TOLEDO, t, 20, 0, 10, retrieved=run_at)
        for t in expected_period_times(run_at, 1)
    ] + [
        record(TOLEDO, datetime(2026, 11, 12, 6, tzinfo=UTC),  # 07:00 local
               None, None, None, retrieved=run_at),
        record(TOLEDO, datetime(2026, 11, 13, 12, tzinfo=UTC),  # day two
               None, 100, 90, retrieved=run_at),
    ]
    row = analyse_destinations(
        [CATALOG[TOLEDO]], {TOLEDO: records}, prefs(), run_at
    )[0]
    assert row["status"] == "available"
    assert row["weather_match_pct"] == 100
    assert row["max_precipitation_probability_pct"] == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "20"])
def test_malformed_metrics_cannot_enter_analysis(value):
    with pytest.raises((TypeError, ValueError)):
        record(TOLEDO, datetime(2026, 11, 12, 9, tzinfo=UTC), value, 0, 10,
               retrieved=datetime(2026, 11, 12, 6, tzinfo=UTC))


def test_two_partial_fetch_groups_are_never_stitched():
    # Two responses for one city, each holding a different half of the
    # needed slots; together they would "cover" the window.
    run_at = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
    times = expected_period_times(run_at, 1)
    first = [record(TOLEDO, times[0], 20, 0, 10, retrieved=run_at)]
    second = [
        record(TOLEDO, t, 20, 0, 10, retrieved=run_at,
               fetch_id="00000000-0000-4000-8000-0000000000c4")
        for t in times[1:]
    ]
    toledo = CATALOG[TOLEDO]
    for records in (first, second):
        row = analyse_destinations(
            [toledo], {TOLEDO: records}, prefs(), run_at
        )[0]
        assert row["reason"] == "missing_periods"
    row = analyse_destinations(
        [toledo], {TOLEDO: first + second}, prefs(), run_at
    )[0]
    assert (row["status"], row["reason"]) == ("unavailable", "invalid_data")


# --- 3. Searcher ranking uses unrounded scores


def test_unrounded_final_score_decides_before_weather_match():
    # Three days, nine slots. Segovia (75 min) passes 26/27 checks:
    # 2600/27 - 1.25 = 95.0463; Seville (351 min, penalty capped at 5)
    # passes 27/27: 100 - 5 = 95.0. Both display as 95.0, and on rounded
    # scores Seville would win on weather match; unrounded, Segovia wins.
    run_at = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
    times = expected_period_times(run_at, 3)
    good = [record(SEVILLE, t, 20, 0, 10, retrieved=run_at) for t in times]
    near = [record(SEGOVIA, t, 20, 0, 10, retrieved=run_at,
                   fetch_id="00000000-0000-4000-8000-0000000000c5")
            for t in times]
    near[4] = record(SEGOVIA, times[4], 20, 0, 26, retrieved=run_at,
                     fetch_id="00000000-0000-4000-8000-0000000000c5")
    rows = analyse_destinations(
        [CATALOG[SEVILLE], CATALOG[SEGOVIA]],
        {SEVILLE: good, SEGOVIA: near}, prefs(3), run_at,
    )
    assert [r["city_id"] for r in rows] == [SEGOVIA, SEVILLE]
    assert rows[0]["final_score"] == pytest.approx(2600 / 27 - 75 / 60)
    assert rows[1]["final_score"] == pytest.approx(95)
    assert round(rows[0]["final_score"], 1) == round(rows[1]["final_score"], 1)
    assert rows[0]["all_preferences_pct"] == pytest.approx(800 / 9)
    # The Dashboard ranks the same rows by weather alone: Seville first.
    assert weather_ranks(rows) == {SEVILLE: 1, SEGOVIA: 2}


# --- 4/5. genuine saved forecasts, replayed read-only

# The last response of the 82-destination P2.5 / P4.4 collection on
# 12 November 2026; every group saved up to then is replayed at this time.
REFERENCE = datetime.fromisoformat("2026-11-12T12:37:35.318886+00:00")
# November is CET (UTC+1): 09:00-18:00 Madrid holds the 09/12/15 UTC slots.
NOVEMBER_DAYTIME_UTC_HOURS = (9, 12, 15)
_METRICS = ("temperature_c", "precipitation_probability_pct", "wind_kmh")


def _stamp(text):
    return datetime.fromisoformat(text).astimezone(UTC)


@pytest.fixture(scope="module")
def genuine():
    """Latest forecast group per city retrieved by REFERENCE, as raw rows."""
    before = WEATHER_RECORDS_PATH.read_bytes()
    with WEATHER_RECORDS_PATH.open(newline="", encoding="utf-8") as file:
        rows = [r for r in csv.DictReader(file) if r["kind"] == "forecast"]
    groups = defaultdict(list)
    for row in rows:
        if _stamp(row["retrieved_at_utc"]) <= REFERENCE:
            groups[(row["city_id"], row["fetch_id"])].append(row)
    latest = {}
    for (city, _), group in groups.items():
        retrieved = _stamp(group[0]["retrieved_at_utc"])
        if city not in latest or retrieved > latest[city][0]:
            latest[city] = (retrieved, group)
    yield {city: group for city, (_, group) in latest.items()}
    assert WEATHER_RECORDS_PATH.read_bytes() == before  # read-only


def _engine_input(genuine):
    wanted = {group[0]["fetch_id"] for group in genuine.values()}
    forecasts = defaultdict(list)
    for r in WeatherStore().load(kind="forecast"):
        if r.fetch_id in wanted:
            forecasts[r.city_id].append(r)
    return forecasts


def _tally(group, days, low, high, rain, wind):
    """Independent hand rule from the raw CSV text for one city."""
    end = REFERENCE + timedelta(hours=24 * days)
    by_time = {_stamp(r["valid_at_utc"]): r for r in group}
    slots, moment = [], REFERENCE.replace(minute=0, second=0, microsecond=0)
    while moment <= end:
        if moment > REFERENCE and moment.hour in NOVEMBER_DAYTIME_UTC_HOURS:
            slots.append(moment)
        moment += timedelta(hours=1)
    if any(t not in by_time for t in slots):
        return {"reason": "missing_periods"}
    cells = [[by_time[t][m] for m in _METRICS] for t in slots]
    if any(c == "" for row in cells for c in row):
        return {"reason": "missing_metrics"}
    values = [tuple(float(c) for c in row) for row in cells]
    checks = [(low <= t <= high, p <= rain, w <= wind) for t, p, w in values]
    passed = sum(sum(c) for c in checks)
    return {
        "reason": None,
        "slots": len(slots),
        "match": 100 * passed / (3 * len(slots)),
        "all": 100 * sum(all(c) for c in checks) / len(slots),
        "mean_t": sum(v[0] for v in values) / len(values),
        "max_p": max(v[1] for v in values),
        "max_w": max(v[2] for v in values),
    }


def _competition_ranks(scores):
    return {
        city: 1 + sum(other > score for other in scores.values())
        for city, score in scores.items()
    }


@pytest.mark.parametrize("days", [1, 2, 3, 4, 5])
def test_genuine_catalog_replay_matches_an_independent_tally(genuine, days):
    assert len(genuine) == 82 and "ES-08019" not in genuine  # Barcelona
    criteria = overview_preferences(
        REFERENCE, load_product_defaults(), days
    )  # Dashboard: autumn 16-24 C, <=30 %, <=25 km/h
    assert (criteria.temperature_min_c, criteria.temperature_max_c) == (
        16, 24)
    destinations = list(CATALOG.values())
    rows = analyse_destinations(
        destinations, _engine_input(genuine), criteria, REFERENCE
    )
    by_city = {r["city_id"]: r for r in rows}
    expected = {
        city: _tally(group, days, 16, 24, 30, 25)
        for city, group in genuine.items()
    }

    assert by_city["ES-08019"]["reason"] == "fetch_failed"
    for city, want in expected.items():
        got = by_city[city]
        assert got["reason"] == want["reason"], city
        if want["reason"]:
            assert got["final_score"] is None
            continue
        assert got["evaluated_periods"] == want["slots"] == 3 * days
        assert got["weather_match_pct"] == pytest.approx(want["match"])
        assert got["all_preferences_pct"] == pytest.approx(want["all"])
        assert got["mean_temperature_c"] == pytest.approx(want["mean_t"])
        assert got["max_precipitation_probability_pct"] == pytest.approx(
            want["max_p"])
        assert got["max_wind_kmh"] == pytest.approx(want["max_w"])
        penalty = min(CATALOG[city].car_duration_min / 60, 5)
        assert got["final_score"] == pytest.approx(
            max(want["match"] - penalty, 0))

    # Searcher order: final desc, match desc, minutes asc, city_id asc.
    ok = [c for c, w in expected.items() if w["reason"] is None]
    trip = sorted(ok, key=lambda c: (
        -max(expected[c]["match"]
             - min(CATALOG[c].car_duration_min / 60, 5), 0),
        -expected[c]["match"], CATALOG[c].car_duration_min, c))
    assert [r["city_id"] for r in rows[:len(ok)]] == trip
    assert all(r["status"] == "unavailable" for r in rows[len(ok):])

    # Dashboard: weather-only competition ranks, city_id within ties, and
    # display filters never change a rank.
    want_ranks = _competition_ranks({c: expected[c]["match"] for c in ok})
    assert weather_ranks(rows) == want_ranks
    frame = prepare_frame(rows, CATALOG_ROWS)
    ranked = frame[frame["rank"].notna()]
    assert ranked["city_id"].tolist() == sorted(
        ok, key=lambda c: (want_ranks[c], c))
    coast = filter_frame(frame, activities=["Coast"])
    assert 0 < len(coast) < len(frame)
    assert coast["rank"].fillna(0).tolist() == [
        want_ranks.get(c, 0) for c in coast["city_id"]
    ]


def test_genuine_fifth_day_needs_a_newer_forecast(genuine):
    # The three P2.5 groups were retrieved at 11:29; their last slot is
    # 17 Nov 09:00, but the five-day window from 12:37 needs 17 Nov 12:00.
    rows = analyse_destinations(
        list(CATALOG.values()), _engine_input(genuine), prefs(5), REFERENCE
    )
    short = {r["city_id"] for r in rows if r["reason"] == "missing_periods"}
    assert short == {TOLEDO, SEGOVIA, SEVILLE}
    for city in short:
        last = max(_stamp(r["valid_at_utc"]) for r in genuine[city])
        assert last == datetime(2026, 11, 17, 9, tzinfo=UTC)
