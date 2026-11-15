"""Adversarial audit: real service/store paths and independent expectations."""

from datetime import datetime, timedelta, timezone

import pytest
import requests

from weather_fakes import (
    Clock, FakeResponse, FakeSession, TOLEDO, SEGOVIA,
    forecast_payload, make_client,
)
from weather_app.config import load_product_defaults
from weather_app.searcher import initial_preferences, search_destinations
from weather_app.service import WeatherService
from weather_app.storage import StorageError, WeatherStore

NOW = datetime(2026, 11, 14, 6, tzinfo=timezone.utc)


@pytest.mark.parametrize("status,code", [
    (401, "authentication"), (429, "rate_limited"), (200, "storage"),
])
def test_cached_coverage_refresh_respects_batch_stop(
    tmp_path, monkeypatch, status, code,
):
    def blocked(*args, **kwargs):
        raise AssertionError("Live HTTP forbidden in audit")

    monkeypatch.setattr(requests.Session, "request", blocked)
    clock = Clock(NOW)
    # Enough fake responses to expose an unwanted second request, not a
    # mock of scoring or forecast_many. Toledo has a fresh incomplete batch.
    payload = forecast_payload(SEGOVIA, NOW + timedelta(hours=3))
    session = FakeSession(FakeResponse(status, payload),
                          FakeResponse(status, payload))
    client = make_client(session, clock)
    store = WeatherStore(tmp_path / "weather.csv")
    records = client.map_forecast(
        TOLEDO, forecast_payload(TOLEDO, NOW + timedelta(hours=3)), NOW
    )
    store.append(records[1:])  # deliberately omit the first required slot
    original = store.path.read_bytes()
    if code == "storage":
        def denied(records):
            raise StorageError("Synthetic save failure")
        monkeypatch.setattr(store, "append", denied)
    service = WeatherService(client, store, clock=clock)
    result = search_destinations(
        [TOLEDO, SEGOVIA], initial_preferences(NOW, load_product_defaults()),
        service, NOW,
    )
    assert len(session.calls) == 1  # Segovia stops all later HTTP work
    assert result["errors"] == {SEGOVIA.city_id: code}
    assert next(r for r in result["rows"] if r["city_id"] == TOLEDO.city_id)[
        "reason"
    ] == "missing_periods"
    assert store.path.read_bytes() == original


def test_reference_categories_seed_the_same_scoring_and_controls():
    from copy import deepcopy
    from weather_app.searcher import RAIN_CHOICES, WIND_CHOICES
    # A valid changed reference must not silently pair Low/Moderate scoring
    # with High/Gentle control codes. No UI or scoring function is mocked.
    defaults = deepcopy(load_product_defaults())
    defaults["max_precipitation_probability_percent"] = 100
    defaults["max_wind_kmh"] = 10
    preferences = initial_preferences(NOW, defaults)
    assert preferences.rain_preference == "High"
    assert preferences.wind_preference == "Gentle"
    rain_label = RAIN_CHOICES[preferences.max_precipitation_probability_pct]
    assert rain_label.startswith("High ")
    assert WIND_CHOICES[preferences.max_wind_kmh].startswith("Gentle ")
