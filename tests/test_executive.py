"""Independent executive answers; synthetic fixtures never enter real data."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from test_analytics import RUN_AT, prefs, record, worked_forecasts
from weather_fakes import CATALOG, TOLEDO, SEGOVIA

from weather_app.analytics import analyse_destinations, daily_weather
from weather_app.config import load_product_defaults, seasonal_defaults
from weather_app.executive import executive_summary, decision_signal


def test_summary_counts_thresholds_ties_and_missing():
    places = [TOLEDO, SEGOVIA, CATALOG["ES-41091"], CATALOG["ES-28005"]]
    rows = analyse_destinations(places, worked_forecasts(), prefs(), RUN_AT)
    result = executive_summary(rows, places)
    assert (result["available"], result["total"]) == (3, 4)
    assert result["average_score"] == pytest.approx(93.12333333333333)
    # Independent nine-slot means, not averages of each city's maxima.
    assert result["average_rain_probability_pct"] == pytest.approx(192 / 9)
    assert result["average_wind_kmh"] == pytest.approx(177 / 9)
    assert [r["rank"] for r in result["rows"]] == [1, 2, 3]
    assert result["leaders"][0]["city_id"] == TOLEDO.city_id
    assert 'Among 3 ranked destinations' in decision_signal(result)


def test_no_data_is_not_zero_risk_or_zero_score():
    result = executive_summary([], [TOLEDO])
    assert result["available"] == 0
    assert result["average_score"] is None
    assert result["average_rain_probability_pct"] is None
    assert result["average_wind_kmh"] is None
    assert not result["leaders"]
    assert 'No complete usable forecasts' in decision_signal(result)


@pytest.mark.parametrize('minutes,band', [
    (119, 'Under 2 hours'), (120, '2–under 4 hours'),
    (239, '2–under 4 hours'), (240, '4–under 6 hours'),
    (359, '4–under 6 hours'), (360, '6 hours or more'),
])
def test_exact_band_boundaries(minutes, band):
    place = replace(TOLEDO, car_duration_min=minutes)
    rows = analyse_destinations([place], worked_forecasts(), prefs(), RUN_AT)
    result = executive_summary(rows, [place])
    assert [label for label, values in result["bands"].items()
            if values] == [band]
    assert result['rows'][0]['weather_match_pct'] == 100


def test_daily_fifth_day_uses_load_time_and_marks_partial_day():
    records = [
        record(TOLEDO.city_id, datetime(2026, 11, 12, hour,
               tzinfo=timezone.utc) + timedelta(days=day),
               20 if day % 2 == 0 else 30, 30, 25)
        for day in range(5) for hour in (9, 12, 15)
    ]
    cells = daily_weather([TOLEDO], {TOLEDO.city_id: records},
                          prefs(days=5), RUN_AT)
    assert [c['score'] for c in cells] == pytest.approx(
        [value - 61 / 30 for value in [100, 79.75, 100, 79.75, 100]])
    assert all(c['evaluated_periods'] == 3 for c in cells)
    cells = daily_weather([TOLEDO], {TOLEDO.city_id: records[:-1]},
                          prefs(days=5), RUN_AT)
    assert cells[-1]['score'] is None
    assert cells[-1]['reason'] == 'missing_periods'
    assert cells[0]['score'] == pytest.approx(100 - 61 / 30)


def test_stale_batch_never_becomes_a_valid_daily_cell():
    old = RUN_AT - timedelta(hours=4)
    forecasts = {TOLEDO.city_id: [
        replace(r, retrieved_at_utc=old)
        for r in worked_forecasts()[TOLEDO.city_id]
    ]}
    cells = daily_weather([TOLEDO], forecasts, prefs(), RUN_AT)
    assert cells[0]['reason'] == 'stale_forecast'
    assert cells[0]['score'] is None


def test_daily_clock_change_uses_madrid_daytime():
    start = datetime(2026, 10, 24, 6, tzinfo=timezone.utc)
    # Oct 24 CEST: 09/12/15 local; Oct 25 CET: 10/13/16 local.
    times = [datetime(2026, 10, 24, h, tzinfo=timezone.utc)
             for h in (9, 12, 15)] + [
        datetime(2026, 10, 25, h, tzinfo=timezone.utc) for h in (9, 12, 15)]
    # At 06 UTC the 07 UTC local-09 slot is not on the provider's grid.
    forecasts = {TOLEDO.city_id: [
        record(TOLEDO.city_id, t, 20, 0, 0, retrieved=start) for t in times
    ]}
    cells = daily_weather([TOLEDO], forecasts, prefs(days=2), start)
    assert [c['score'] for c in cells] == pytest.approx(
        [100 - 61 / 30, 100 - 61 / 30])
    assert [c['expected_periods'] for c in cells] == [3, 3]


def test_season_uses_shared_reference_and_madrid_boundary():
    defaults = load_product_defaults()
    moment = datetime(2026, 11, 30, 23, 30, tzinfo=timezone.utc)
    name, season = seasonal_defaults(moment, defaults)
    assert (name, season['min'], season['max']) == ('Winter', 10, 18)
    with pytest.raises(ValueError):
        seasonal_defaults(moment.replace(tzinfo=None), defaults)


def test_daily_average_order_preserves_missing_days_ties_and_zero():
    from weather_app.executive import daily_score_order
    places = [replace(TOLEDO, city_id=f'ES-{90000 + i:05d}') for i in range(5)]
    scores = [[100, 60, 80], [90, None, None], [0, 0, 0],
              [None, None, None], [70, 80, 90]]
    cells = [dict(city_id=place.city_id, day=day, score=score)
             for place, values in zip(places, scores)
             for day, score in enumerate(values, 1)]
    result = daily_score_order(cells, places[::-1])
    assert [r['city_id'] for r in result] == [
        'ES-90001', 'ES-90000', 'ES-90004', 'ES-90002', 'ES-90003']
    assert [r['average_score'] for r in result] == [90, 80, 80, 0, None]
    assert result[0]['available_days'] == 1
    assert all(r['total_days'] == 3 for r in result)
    assert result[-1]['available_days'] == 0
    assert all(r['average_score'] is None
               for r in daily_score_order([], places))


def test_daily_average_order_uses_unrounded_scores():
    from weather_app.executive import daily_score_order
    a = replace(TOLEDO, city_id='ES-90000')
    b = replace(TOLEDO, city_id='ES-90001')
    result = daily_score_order([
        dict(city_id='ES-90000', day=1, score=80.01),
        dict(city_id='ES-90001', day=1, score=80.04),
    ], [a, b])
    assert [r['city_id'] for r in result] == ['ES-90001', 'ES-90000']


@pytest.fixture(scope="module")
def genuine_snapshot():
    """Read once, group in linear time, share immutable genuine inputs only."""
    from collections import defaultdict
    from types import MappingProxyType
    from weather_app.storage import WeatherStore, load_destinations

    catalog = tuple(load_destinations())
    records = WeatherStore().load(kind="forecast")
    at = max(r.retrieved_at_utc for r in records)
    groups = defaultdict(list)
    for item in records:
        groups[item.city_id].append(item)
    forecasts = {}
    for place in catalog:
        candidates = groups[place.city_id]
        latest = max(r.retrieved_at_utc for r in candidates)
        forecasts[place.city_id] = tuple(
            r for r in candidates if r.retrieved_at_utc == latest)
    return catalog, at, MappingProxyType(forecasts)


@pytest.mark.parametrize("days", [1, 2, 3, 4, 5])
def test_genuine_snapshot_has_one_dashboard_score_across_views(
    days, genuine_snapshot,
):
    from weather_app.dashboard import (
        overview_preferences, prepare_frame, map_points, _catalogue_table,
    )
    from weather_app.executive_view import scatter_figure

    catalog, at, forecasts = genuine_snapshot
    preferences = overview_preferences(at, load_product_defaults(), days)
    rows = analyse_destinations(catalog, forecasts, preferences, at)
    canonical = {r["city_id"]: r for r in rows}
    # Avoid a vacuous pass if a regression makes every result unavailable.
    assert any(r["status"] == "available" for r in rows)
    assert len(rows) == len(catalog)
    catalog_rows = [d.as_catalog_row() for d in catalog]
    frame = prepare_frame(rows, catalog_rows)
    summary = executive_summary(rows, catalog)
    points = {p["city_id"]: p for p in map_points(catalog_rows, frame)}
    table = _catalogue_table(frame, catalog, {}, at)
    scatter = scatter_figure(summary["rows"])
    assert "Weather comfort / 100" not in table.columns
    assert list(scatter.data[0].y) == [
        r["final_score"] for r in summary["rows"]]
    for index, row in frame.iterrows():
        original = canonical[row["city_id"]]
        if original["status"] != "available":
            continue
        score = original["final_score"]
        assert 0 <= score <= 100
        assert points[row["city_id"]]["weather_score"] == score
        assert table.loc[index, "Destination score / 100"] == score
        assert points[row["city_id"]]["rank"] == row["rank"]
    for row in summary["rows"]:
        assert row["final_score"] == canonical[row["city_id"]]["final_score"]
        assert row["rank"] == points[row["city_id"]]["rank"]
    for band in summary["bands"].values():
        for row in band:
            assert row["final_score"] == canonical[
                row["city_id"]]["final_score"]
    if days == 1:
        # Identical time windows must give identical heatmap/window scores.
        daily = daily_weather(catalog, forecasts, preferences, at)
        assert {c["city_id"]: c["score"] for c in daily} == {
            r["city_id"]: r["final_score"] for r in rows}
