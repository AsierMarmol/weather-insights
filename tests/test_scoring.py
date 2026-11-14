"""Independent comfort-v2 examples, boundaries and mode separation."""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from test_analytics import prefs, record, RUN_AT, DAY_PERIODS
from weather_fakes import TOLEDO
from weather_app.analytics import analyse_destinations, daily_weather
from weather_app.scoring import (
    aggregate, dashboard_wind_score, range_score, slot_score, wind_label,
)


@pytest.mark.parametrize("speed,score", [
    (0, 100), (10, 100), (15, 92.5), (20, 85), (25, 72.5),
    (30, 60), (40, 30), (50, 15), (60, 0), (100, 0),
])
def test_wind_interpolation(speed, score):
    assert dashboard_wind_score(speed) == score


@pytest.mark.parametrize("temperature,score", [
    (-10, 0), (14, 90), (16, 100), (24, 100), (25, 92.5), (50, 0),
])
def test_temperature_declines_gradually(temperature, score):
    assert range_score(temperature, 16, 24, 5, 7.5) == score


def test_aggregate_uses_ceiling_and_does_not_round():
    # Five slots -> worst two (0 and 50); 80%*70 + 20%*25 = 61.
    assert aggregate([0, 50, 100, 100, 100]) == 61
    assert aggregate([80.001]) == pytest.approx(80.001)
    with pytest.raises(ValueError):
        aggregate([])


def test_high_and_medium_rain_are_targets_not_maximums():
    p = prefs(rain_preference="Medium", wind_preference="Moderate")
    dry = record(TOLEDO.city_id, DAY_PERIODS[0], 20, 0, 25)
    mid = replace(dry, precipitation_probability_pct=45)
    wet = replace(dry, precipitation_probability_pct=90)
    assert slot_score(mid, p)[0] == 100
    assert slot_score(dry, p)[0] == slot_score(wet, p)[0] == 79
    high = replace(p, rain_preference="High")
    assert slot_score(wet, high)[0] == 100
    assert slot_score(dry, high)[0] == 65


def test_medium_wind_rewards_band_and_declines_both_sides():
    p = prefs(rain_preference="Low", wind_preference="Moderate")
    r = record(TOLEDO.city_id, DAY_PERIODS[0], 20, 0, 25)
    assert slot_score(r, p)[0] == 100
    assert slot_score(replace(r, wind_kmh=10), p)[0] == 90
    assert slot_score(replace(r, wind_kmh=39), p)[0] == 90


def test_exact_category_boundaries_and_continuity():
    p = prefs(rain_preference="Medium", wind_preference="Moderate")
    r = record(TOLEDO.city_id, DAY_PERIODS[0], 20, 30, 29)
    score, flags = slot_score(r, p)
    assert score == 100  # continuous at the shared range boundaries
    assert flags == (True, False, False)  # labels have exact ownership
    assert wind_label(19.9) == "Gentle"
    assert wind_label(20) == "Moderate"
    assert wind_label(29) == "Fresh"
    assert wind_label(39) == "Strong"
    assert wind_label(50) == "Near gale or stronger"


def test_dashboard_weights_cloud_penalty_and_mode_independence():
    p = prefs(scoring_mode="dashboard")
    r = replace(record(TOLEDO.city_id, DAY_PERIODS[0], 25, 20, 20),
                cloud_pct=50)
    # 45%*92.5 + 35%*80 + 15%*85 + 5%*50 = 84.875.
    assert slot_score(r, p)[0] == 84.875
    assert slot_score(replace(r, cloud_pct=0), p)[0] == 87.375
    assert slot_score(replace(r, cloud_pct=100), p)[0] == 82.375
    assert slot_score(r, replace(p, rain_preference="High"))[0] == 84.875


def test_dashboard_uses_each_slots_madrid_season_searcher_stays_fixed():
    before = datetime(2026, 11, 30, 22, 59, tzinfo=timezone.utc)
    after = datetime(2026, 11, 30, 23, 0, tzinfo=timezone.utc)
    r = replace(record(TOLEDO.city_id, before, 24, 0, 0), cloud_pct=0)
    p = prefs(scoring_mode="dashboard")
    assert slot_score(r, p)[0] == 100
    assert slot_score(replace(r, valid_at_utc=after), p)[0] == 79.75
    assert slot_score(replace(r, valid_at_utc=after), prefs())[0] == 100


def test_missing_cloud_blocks_dashboard_only_and_travel_is_capped():
    records = [replace(record(TOLEDO.city_id, t, 20, 0, 0), cloud_pct=None)
               for t in DAY_PERIODS]
    data = {TOLEDO.city_id: records}
    row = analyse_destinations([TOLEDO], data, prefs(), RUN_AT)[0]
    assert row['weather_match_pct'] == 100
    assert row['travel_penalty'] == pytest.approx(61 / 30)
    missing = analyse_destinations(
        [TOLEDO], data, prefs(scoring_mode="dashboard"), RUN_AT)[0]
    assert missing['reason'] == 'missing_metrics'
    assert missing['final_score'] is None
    far = replace(TOLEDO, car_duration_min=600)
    far_row = analyse_destinations([far], data, prefs(), RUN_AT)[0]
    assert far_row['final_score'] == 85


def test_new_forecast_changes_scores_and_daily_score_includes_driving():
    clear = [replace(record(TOLEDO.city_id, t, 20, 0, 0), cloud_pct=0)
             for t in DAY_PERIODS]
    wet = [replace(r, precipitation_probability_pct=100) for r in clear]
    p = prefs(scoring_mode="dashboard")
    for records, expected in [(clear, 100), (wet, 65)]:
        data = {TOLEDO.city_id: records}
        row = analyse_destinations([TOLEDO], data, p, RUN_AT)[0]
        assert row['weather_match_pct'] == expected
        assert row['final_score'] == pytest.approx(expected - 61 / 30)
        assert daily_weather([TOLEDO], data, p, RUN_AT)[0]['score'] == (
            pytest.approx(expected - 61 / 30))


@pytest.mark.parametrize('kwargs', [
    {'scoring_mode': 'unknown'}, {'rain_preference': 'unknown'},
    {'wind_preference': 'unknown'}, {'seasonal_bands': ((10, 18),)},
])
def test_invalid_scoring_preferences_rejected(kwargs):
    with pytest.raises(ValueError):
        prefs(**kwargs)


def test_shared_season_defaults_match_dashboard_month_mapping():
    from weather_app.config import load_product_defaults
    from weather_app.dashboard import overview_preferences
    from weather_app.scoring import SEASONAL_BANDS
    p = overview_preferences(RUN_AT, load_product_defaults(), 3)
    assert p.seasonal_bands == SEASONAL_BANDS
    assert p.scoring_mode == "dashboard"
    assert p.rain_preference is p.wind_preference is None
