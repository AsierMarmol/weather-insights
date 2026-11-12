"""Offline checks for the P2.3 diagnostic tool; fixtures are not weather
history.
"""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests

spec = importlib.util.spec_from_file_location(
    "api_verification",
    Path(__file__).resolve().parents[1] / "scripts/verify_weather_access.py",
)
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)


def forecast_fixture():
    # Hand-specified winter grid. Local daytime covers 09:00, 12:00, 15:00 UTC.
    start = int(datetime(2026, 1, 1, 3, tzinfo=timezone.utc).timestamp())
    return {
        "list": [
            {
                "dt": start + n * 10800,
                "main": {"temp": 15},
                "wind": {"speed": 3},
                "pop": 0.2,
            }
            for n in range(40)
        ]
    }


def test_complete_windows_and_missing_next_day():
    run = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    payload = forecast_fixture()
    result = verification.coverage(payload, run)
    assert [
        result[f"daytime_{h}h"]["expected_periods"]
        for h in (24, 48, 72, 96, 120)
    ] == [3, 6, 9, 12, 15]
    assert all(
        result[f"daytime_{h}h"]["complete"] for h in (24, 48, 72, 96, 120)
    )
    missing = int(datetime(2026, 1, 2, 9, tzinfo=timezone.utc).timestamp())
    payload["list"] = [p for p in payload["list"] if p["dt"] != missing]
    result = verification.coverage(payload, run)
    assert result["daytime_24h"]["complete"]
    assert not result["daytime_48h"]["complete"]
    assert not result["daytime_72h"]["complete"]
    assert not result["unique_sorted_3h_grid"]


def test_missing_fifth_day_is_not_silently_shortened():
    payload = forecast_fixture()
    missing = int(datetime(2026, 1, 5, 12, tzinfo=timezone.utc).timestamp())
    payload["list"] = [p for p in payload["list"] if p["dt"] != missing]
    result = verification.coverage(
        payload, datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    )
    assert all(result[f"daytime_{h}h"]["complete"] for h in (24, 48, 72, 96))
    assert result["daytime_120h"]["expected_periods"] == 15
    assert not result["daytime_120h"]["complete"]


def test_five_day_window_across_madrid_clock_change():
    run = datetime(2026, 3, 27, 22, 15, tzinfo=timezone.utc)
    first = int(datetime(2026, 3, 28, 0, tzinfo=timezone.utc).timestamp())
    payload = {
        "list": [
            {
                "dt": first + n * 10800,
                "main": {"temp": 15},
                "wind": {"speed": 3},
                "pop": 0.2,
            }
            for n in range(40)
        ]
    }
    result = verification.coverage(payload, run)
    assert result["unique_sorted_3h_grid"]
    assert [
        result[f"daytime_{h}h"]["expected_periods"]
        for h in (24, 48, 72, 96, 120)
    ] == [3, 6, 9, 12, 15]
    assert all(
        result[f"daytime_{h}h"]["complete"] for h in (24, 48, 72, 96, 120)
    )


def test_missing_probability_cannot_pass_as_dry_weather():
    payload = forecast_fixture()
    del payload["list"][0]["pop"]
    result = verification.coverage(
        payload, datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    assert not result["valid_required_fields"]


def test_redacts_nested_credentials_and_echoes():
    secret = "test-secret-not-real"
    payload = {
        "appid": secret,
        "nested": [{"API_KEY": secret, "message": f"echo {secret}"}],
    }
    clean = verification.redact(payload, secret)
    assert secret not in json.dumps(clean)
    assert clean == {"nested": [{"message": "echo [REDACTED]"}]}


def test_location_accents_match_but_translation_needs_review():
    payload = {
        "name": "Malaga",
        "coord": {"lat": 36.72, "lon": -4.42},
        "sys": {"country": "ES"},
    }
    result = verification.location_check(
        payload, "weather", 36.72, -4.42, "Málaga"
    )
    assert result["name_matches_normalized"] and not result["review_required"]
    payload["name"] = "Different nearby town"
    result = verification.location_check(
        payload, "weather", 36.72, -4.42, "Málaga"
    )
    assert result["within_10km"] and result["review_required"]


def test_matching_name_does_not_hide_wrong_forecast_coordinates():
    payload = {
        "city": {
            "name": "Toledo",
            "country": "US",
            "coord": {"lat": 41.65, "lon": -83.54},
        }
    }
    result = verification.location_check(
        payload, "forecast", 39.86, -4.02, "Toledo"
    )
    assert result["name_matches_normalized"]
    assert not result["within_10km"] and result["review_required"]


def test_explicit_provider_alias_and_city_id_override():
    city = {"latitude": "40", "longitude": "-4"}
    assert verification.request_parameters(city, {}) == {"lat": 40, "lon": -4}
    assert verification.request_parameters(
        city, {"request_parameters": {"id": 12345}}
    ) == {"id": 12345}
    with pytest.raises(ValueError):
        verification.request_parameters(
            city, {"request_parameters": {"q": "Example"}}
        )
    payload = {
        "name": "Vitoria-Gasteiz",
        "coord": {"lat": 42.85, "lon": -2.67},
        "sys": {"country": "ES"},
        "id": 1,
    }
    check = verification.location_check(
        payload,
        "weather",
        42.85,
        -2.67,
        "Gasteiz / Vitoria",
        ["Vitoria-Gasteiz"],
        1,
    )
    assert check["accepted_provider_alias"] and not check["review_required"]
    check = verification.location_check(
        payload,
        "weather",
        42.85,
        -2.67,
        "Gasteiz / Vitoria",
        ["Vitoria-Gasteiz"],
        2,
    )
    assert check["review_required"] and not check["provider_id_matches"]


@pytest.mark.parametrize("status", [401, 404, 429, 503])
def test_http_failures_do_not_store_observations(
    tmp_path, monkeypatch, status
):
    monkeypatch.setattr(verification, "DATA", tmp_path)

    class Response:
        status_code = status

        def json(self):
            pytest.fail("Error response body must not be read or logged")

    class Session:
        def get(self, *args, **kwargs):
            assert kwargs["allow_redirects"] is False
            return Response()

    summary, payload = verification.probe(
        Session(), "weather", {}, "test-secret-not-real", "failure", "test"
    )
    assert summary == {
        "check": "failure",
        "http_status": status,
        "result": "http_error",
    }
    assert payload is None
    assert not list(tmp_path.iterdir())


def test_timeout_exception_text_is_not_exposed(tmp_path, monkeypatch):
    monkeypatch.setattr(verification, "DATA", tmp_path)

    class Session:
        def get(self, *args, **kwargs):
            raise requests.Timeout("URL contains test-secret-not-real")

    summary, payload = verification.probe(
        Session(), "weather", {}, "test-secret-not-real", "slow", "test"
    )
    assert summary == {"check": "slow", "result": "timeout"}
    assert payload is None
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "payload", [None, [], {"city": None}, {"city": {"coord": None}}]
)
def test_malformed_location_requires_review_without_crashing(payload):
    result = verification.location_check(
        payload, "forecast", 40, -4, "Example"
    )
    assert result["review_required"]
    assert not result["within_10km"]


def test_storage_failure_is_not_reported_as_saved(tmp_path, monkeypatch):
    # A file where the data directory should be reproduces an actual OS
    # failure.
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("existing content")
    monkeypatch.setattr(verification, "DATA", blocker)

    class Response:
        status_code = 200

        def json(self):
            return {"dt": 1, "main": {"temp": 20}, "wind": {"speed": 2}}

    class Session:
        def get(self, *args, **kwargs):
            return Response()

    summary, payload = verification.probe(
        Session(), "weather", {}, "dummy", "save", "run"
    )
    assert summary["result"] == "storage_error"
    assert payload is None
    assert blocker.read_text() == "existing content"


def test_non_object_json_does_not_create_weather_record(tmp_path, monkeypatch):
    monkeypatch.setattr(verification, "DATA", tmp_path)

    class Response:
        status_code = 200

        def json(self):
            return ["unexpected response"]

    class Session:
        def get(self, *args, **kwargs):
            return Response()

    summary, payload = verification.probe(
        Session(), "forecast", {}, "dummy", "bad-data", "run"
    )
    assert summary["result"] == "invalid_data" and payload is None
    assert not list(tmp_path.iterdir())
