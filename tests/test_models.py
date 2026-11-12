"""P3.1 model tests. All weather values here are synthetic test inputs."""

import math
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from weather_app.models import (
    RECORD_FIELDS,
    Destination,
    SearchPreferences,
    WeatherRecord,
)

UTC = timezone.utc
FETCH_ID = "5f0c6a3e-8f43-4a43-9c51-3c2f1a1b2c3d"


def toledo(**changes):
    values = dict(
        city_id="ES-45168",
        city="Toledo",
        region="Castilla-La Mancha",
        car_distance_km=72,
        car_duration_min=61,
        latitude=39.8581,
        longitude=-4.02263,
        activities=("History and heritage", "Food and gastronomy"),
        destination_size="Small city or town",
    )
    values.update(changes)
    return Destination(**values)


def preferences(**changes):
    values = dict(
        days=3,
        temperature_min_c=16,
        temperature_max_c=24,
        max_precipitation_probability_pct=30,
        max_wind_kmh=25,
    )
    values.update(changes)
    return SearchPreferences(**values)


def record(**changes):
    values = dict(
        fetch_id=FETCH_ID,
        city_id="ES-45168",
        kind="forecast",
        retrieved_at_utc=datetime(2026, 11, 11, 18, 30, tzinfo=UTC),
        valid_at_utc=datetime(2026, 11, 12, 12, tzinfo=UTC),
        latitude=39.8581,
        longitude=-4.0226,
        temperature_c=20.0,
        wind_kmh=10.548,
        precipitation_probability_pct=30.0,
        humidity_pct=60.0,
        cloud_pct=None,
        provider_city_id=2510409,
        provider_city_name="Toledo",
    )
    values.update(changes)
    return WeatherRecord(**values)


# --- Destination ----------------------------------------------------------------


def test_destination_normalizes_numbers_and_computes_drive_hours():
    destination = toledo()
    assert destination.car_duration_min == 61.0
    assert isinstance(destination.car_distance_km, float)
    assert destination.drive_hours == pytest.approx(61 / 60)
    assert str(destination) == "Toledo (Castilla-La Mancha)"
    assert "ES-45168" in repr(destination) and "drive_hours=1.02" in repr(destination)


def test_destination_catalog_row_uses_activity_list():
    row = toledo().as_catalog_row()
    assert list(row) == [
        "city_id", "city", "region", "car_distance_km", "car_duration_min",
        "latitude", "longitude", "activities", "destination_size",
    ]
    assert row["activities"] == ["History and heritage", "Food and gastronomy"]


def test_destination_is_immutable_and_comparable():
    destination = toledo()
    with pytest.raises(FrozenInstanceError):
        destination.city = "Madrid"
    assert destination == toledo()
    assert len({destination, toledo()}) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"city_id": "45168"},
        {"city": "  "},
        {"car_duration_min": -1},
        {"car_distance_km": True},
        {"car_distance_km": "72"},
        {"latitude": 91},
        {"longitude": math.nan},
        {"activities": ()},
        {"activities": ("Skiing",)},
        {"activities": ("Coast", "Coast")},
        {"activities": "Coast"},
        {"destination_size": "Village"},
    ],
)
def test_destination_rejects_invalid_values(changes):
    with pytest.raises(ValueError):
        toledo(**changes)


# --- SearchPreferences ------------------------------------------------------------


def test_preferences_default_to_all_and_compute_horizon():
    prefs = preferences(activities=["Coast"])
    assert prefs.activities == ("Coast",)
    assert prefs.destination_sizes == ()
    assert prefs.horizon == timedelta(hours=72)
    assert preferences(days=5).horizon == timedelta(hours=120)


def test_preferences_accept_equal_temperature_bounds_and_limits():
    prefs = preferences(temperature_min_c=20, temperature_max_c=20,
                        max_precipitation_probability_pct=0, max_wind_kmh=0)
    assert prefs.temperature_min_c == prefs.temperature_max_c == 20.0


@pytest.mark.parametrize(
    "changes",
    [
        {"days": 0},
        {"days": 6},
        {"days": 2.5},
        {"days": True},
        {"temperature_min_c": 25},
        {"temperature_max_c": math.inf},
        {"max_precipitation_probability_pct": 101},
        {"max_precipitation_probability_pct": -1},
        {"max_wind_kmh": -0.1},
        {"activities": ("Beach",)},
        {"destination_sizes": ("Village",)},
    ],
)
def test_preferences_reject_invalid_values(changes):
    with pytest.raises(ValueError):
        preferences(**changes)


# --- WeatherRecord -------------------------------------------------------------------


def test_record_normalizes_times_to_utc_and_keeps_them_separate():
    madrid = ZoneInfo("Europe/Madrid")
    rec = record(
        retrieved_at_utc=datetime(2026, 11, 11, 19, 30, tzinfo=madrid),
        valid_at_utc=datetime(2026, 11, 12, 13, tzinfo=madrid),
    )
    assert rec.retrieved_at_utc == datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
    assert rec.retrieved_at_utc.tzinfo == UTC
    assert rec.valid_at_utc == datetime(2026, 11, 12, 12, tzinfo=UTC)
    assert rec.lead_time == timedelta(hours=17, minutes=30)


def test_record_keeps_missing_metrics_as_none():
    rec = record(temperature_c=None, wind_kmh=None, precipitation_probability_pct=None)
    assert rec.temperature_c is None and rec.wind_kmh is None
    assert "n/a" in str(rec)


def test_record_csv_round_trip_is_exact():
    rec = record(temperature_c=15.87, wind_kmh=2.93 * 3.6)
    row = rec.to_csv_row()
    assert list(row) == list(RECORD_FIELDS)
    assert row["cloud_pct"] == ""  # None is a blank cell, never zero
    assert row["retrieved_at_utc"] == "2026-11-11T18:30:00+00:00"
    assert WeatherRecord.from_csv_row(row) == rec


def test_records_sort_chronologically_and_have_readable_text():
    later = record(valid_at_utc=datetime(2026, 11, 12, 15, tzinfo=UTC))
    earlier = record(valid_at_utc=datetime(2026, 11, 12, 9, tzinfo=UTC))
    assert sorted([later, earlier]) == [earlier, later]
    assert str(earlier) == (
        "forecast ES-45168 at 2026-11-12T09:00:00+00:00: 20 °C, "
        "wind 10.548 km/h, rain probability 30 %"
    )


def test_new_fetch_ids_are_unique_uuids():
    first, second = WeatherRecord.new_fetch_id(), WeatherRecord.new_fetch_id()
    assert first != second
    assert record(fetch_id=first).fetch_id == first


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": 2},
        {"fetch_id": "not-a-uuid"},
        {"city_id": "Toledo"},
        {"kind": "history"},
        {"retrieved_at_utc": datetime(2026, 11, 11, 18, 30)},
        {"valid_at_utc": "2026-11-12T12:00:00+00:00"},
        {"latitude": -91},
        {"temperature_c": math.nan},
        {"temperature_c": True},
        {"wind_kmh": -1},
        {"precipitation_probability_pct": 100.5},
        {"humidity_pct": -5},
        {"provider_city_id": 0},
        {"provider_city_id": "2510409"},
        {"provider_city_name": ""},
        {"kind": "current", "precipitation_probability_pct": 10},
    ],
)
def test_record_rejects_invalid_values(changes):
    with pytest.raises(ValueError):
        record(**changes)


def test_current_observation_is_valid_before_retrieval():
    rec = record(
        kind="current",
        precipitation_probability_pct=None,
        valid_at_utc=datetime(2026, 11, 11, 18, 20, tzinfo=UTC),
    )
    assert rec.lead_time == timedelta(minutes=-10)
    with pytest.raises(ValueError):
        replace(rec, precipitation_probability_pct=0.0)


@pytest.mark.parametrize(
    "field, value",
    [("valid_at_utc", "yesterday"), ("temperature_c", "warm"), ("provider_city_id", "x")],
)
def test_from_csv_row_rejects_malformed_cells(field, value):
    row = record().to_csv_row()
    row[field] = value
    with pytest.raises(ValueError):
        WeatherRecord.from_csv_row(row)


def test_from_csv_row_rejects_naive_timestamps():
    row = record().to_csv_row()
    row["valid_at_utc"] = "2026-11-12T12:00:00"
    with pytest.raises(ValueError):
        WeatherRecord.from_csv_row(row)


# --- schema version (regression: 1.0 used to be accepted and saved as "1.0") ---


def test_integer_schema_version_serializes_and_parses():
    rec = record(schema_version=1)
    assert rec.schema_version == 1 and type(rec.schema_version) is int
    row = rec.to_csv_row()
    assert row["schema_version"] == "1"
    assert WeatherRecord.from_csv_row(row) == rec


@pytest.mark.parametrize("version", [1.0, True, False, "1", 0, 2, -1, None, 1.5])
def test_schema_version_must_be_the_supported_integer(version):
    with pytest.raises(ValueError, match="schema_version"):
        record(schema_version=version)


def test_schema_version_cannot_be_swapped_after_construction():
    with pytest.raises(ValueError, match="schema_version"):
        replace(record(), schema_version=1.0)


@pytest.mark.parametrize("cell", ["1.0", "True", "", "2"])
def test_from_csv_row_rejects_non_integer_or_unsupported_versions(cell):
    row = record().to_csv_row()
    row["schema_version"] = cell
    with pytest.raises(ValueError):
        WeatherRecord.from_csv_row(row)
