"""P3.2 client tests: offline fake sessions, synthetic payloads and read-only genuine replay."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import requests
from weather_fakes import (
    CATALOG,
    DUMMY_KEY,
    LUGO,
    TOLEDO,
    VITORIA,
    Clock,
    FakeResponse,
    FakeSession,
    current_payload,
    forecast_payload,
    make_client,
)

from weather_app import client as client_module
from weather_app import config
from weather_app.client import (
    APIError,
    AuthenticationError,
    InvalidDataError,
    InvalidInputError,
    JSONAPIClient,
    NetworkError,
    OpenWeatherClient,
    RateLimiter,
)
from weather_app.models import WeatherRecord

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 10, 0, tzinfo=UTC)
GENUINE_FETCHES = Path(__file__).resolve().parents[1] / "data" / "weather" / "api_verification_fetches.jsonl"


def raised(callable_, *args):
    with pytest.raises(APIError) as info:
        callable_(*args)
    return info.value


# --- generic base -----------------------------------------------------------------


class OtherProviderClient(JSONAPIClient):
    """A different JSON provider reusing the base with another key parameter."""

    def __init__(self, session):
        super().__init__(
            "https://example.test/api/",
            api_key="other-dummy-key",
            api_key_parameter="api_key",
            session=session,
            rate_limiter=RateLimiter(100, 60),
            sleep=lambda s: None,
        )

    def lookup(self, term):
        return self._get_json("search", {"q": term})


def test_base_is_reusable_by_another_provider():
    session = FakeSession(FakeResponse(200, {"ok": True}))
    assert OtherProviderClient(session).lookup("x") == {"ok": True}
    call = session.calls[0]
    assert call["url"] == "https://example.test/api/search"
    assert call["params"] == {"q": "x", "api_key": "other-dummy-key"}
    assert call["allow_redirects"] is False and call["timeout"] == (5.0, 20.0)


def test_openweather_client_inherits_generic_behavior():
    assert issubclass(OpenWeatherClient, JSONAPIClient)
    session = FakeSession(FakeResponse(200, current_payload(TOLEDO, NOW)))
    client = make_client(session, Clock(NOW))
    client.current(TOLEDO)
    call = session.calls[0]
    assert call["url"] == "https://api.openweathermap.org/data/2.5/weather"
    assert call["params"] == {
        "lat": TOLEDO.latitude,
        "lon": TOLEDO.longitude,
        "units": "metric",
        "lang": "en",
        "appid": DUMMY_KEY,
    }
    assert client.request_count == 1


def test_key_is_private_and_masked():
    client = make_client(FakeSession())
    assert DUMMY_KEY not in repr(client) and "***" in repr(client)
    holders = [name for name, value in vars(client).items() if value == DUMMY_KEY]
    assert holders == ["_JSONAPIClient__api_key"]  # name-mangled, only in the base
    assert not hasattr(client, "api_key") and not hasattr(client, "_api_key")


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (400, "invalid_input"),
        (401, "authentication"),
        (403, "authentication"),
        (404, "location_not_found"),
        (429, "rate_limited"),
        (302, "provider"),
        (418, "provider"),
    ],
)
def test_statuses_map_to_distinct_codes_without_retry(status, code):
    session = FakeSession(FakeResponse(status, {"message": f"secret {DUMMY_KEY}"}))
    error = raised(make_client(session).current, TOLEDO)
    assert error.code == code
    assert len(session.calls) == 1
    assert DUMMY_KEY not in error.message


def test_server_error_is_retried_once_then_reported():
    session = FakeSession(FakeResponse(503), FakeResponse(500))
    error = raised(make_client(session).current, TOLEDO)
    assert error.code == "provider" and "server error" in error.message
    assert len(session.calls) == 2


def test_transient_failure_then_success_uses_one_retry():
    session = FakeSession(requests.Timeout(), FakeResponse(200, current_payload(TOLEDO, NOW)))
    record = make_client(session, Clock(NOW)).current(TOLEDO)
    assert record.city_id == TOLEDO.city_id and len(session.calls) == 2


@pytest.mark.parametrize(
    ("exception", "text"),
    [
        (requests.Timeout(f"https://x/?appid={DUMMY_KEY}"), "did not respond"),
        (requests.ConnectionError(f"https://x/?appid={DUMMY_KEY}"), "Could not connect"),
        (requests.TooManyRedirects(f"https://x/?appid={DUMMY_KEY}"), "could not be completed"),
    ],
)
def test_network_errors_hide_raw_exception_and_key(exception, text):
    session = FakeSession(exception, exception)
    error = raised(make_client(session).current, TOLEDO)
    assert isinstance(error, NetworkError) and text in error.message
    assert DUMMY_KEY not in str(error)
    assert error.__cause__ is None and error.__suppress_context__


@pytest.mark.parametrize("answer", [FakeResponse(200, bad_json=True), FakeResponse(200, ["list"])])
def test_non_object_json_is_invalid_data(answer):
    assert raised(make_client(FakeSession(answer)).current, TOLEDO).code == "invalid_data"


def test_input_is_validated_before_http():
    session = FakeSession()
    client = make_client(session)
    for bad in ("Toledo", None, TOLEDO.as_catalog_row()):
        assert raised(client.current, bad).code == "invalid_input"
    with pytest.raises(InvalidInputError):
        client._get_json("/absolute", {})
    with pytest.raises(InvalidInputError):
        client._get_json("weather", {"appid": "caller-supplied"})
    assert session.calls == []


def test_missing_api_key_is_authentication_guidance(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / "missing.env")
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    with pytest.raises(AuthenticationError, match="variables.env"):
        OpenWeatherClient.from_environment(session=FakeSession())
    with pytest.raises(AuthenticationError):
        JSONAPIClient("https://example.test", api_key="  ", api_key_parameter="k")


# --- pacing -----------------------------------------------------------------------


def test_rate_limiter_caps_calls_per_window():
    moments = iter([0.0, 1.0, 2.0, 60.0])
    slept = []
    limiter = RateLimiter(2, 60.0, clock=lambda: next(moments), sleep=slept.append)
    assert limiter.wait() == 0 and limiter.wait() == 0
    assert limiter.wait() == pytest.approx(58.0)
    assert slept == [pytest.approx(58.0)]


def test_failed_attempts_and_retries_count_against_the_limit():
    waits = []

    class CountingLimiter(RateLimiter):
        def wait(self):
            waits.append(1)
            return 0.0

    session = FakeSession(FakeResponse(500), FakeResponse(500))
    client = make_client(session, rate_limiter=CountingLimiter())
    raised(client.forecast, TOLEDO)
    assert len(waits) == 2


def test_default_limiter_is_one_shared_process_queue():
    first = OpenWeatherClient(DUMMY_KEY, session=FakeSession())
    second = OpenWeatherClient(DUMMY_KEY, session=FakeSession())
    assert first._rate_limiter is second._rate_limiter is client_module.OPENWEATHER_RATE_LIMITER
    assert client_module.OPENWEATHER_RATE_LIMITER.max_calls == 40


# --- request parameters and mapping -----------------------------------------------------


def test_lugo_uses_verified_provider_city_id():
    params = make_client(FakeSession()).request_parameters(LUGO)
    assert params == {"id": 3117814, "units": "metric", "lang": "en"}


def test_current_mapping_units_and_timestamps():
    retrieved = NOW + timedelta(seconds=1)
    session = FakeSession(FakeResponse(200, current_payload(TOLEDO, NOW - timedelta(minutes=10))))
    record = make_client(session, Clock(retrieved)).current(TOLEDO)
    assert isinstance(record, WeatherRecord) and record.kind == "current"
    assert record.temperature_c == 21.5
    assert record.wind_kmh == 18.0  # 5 m/s * 3.6
    assert record.precipitation_probability_pct is None
    assert (record.humidity_pct, record.cloud_pct) == (40.0, 20.0)
    assert record.retrieved_at_utc == retrieved
    assert record.valid_at_utc == NOW - timedelta(minutes=10)
    assert record.valid_at_utc.tzinfo is not None
    assert (record.provider_city_id, record.provider_city_name) == (2510409, "Toledo")


def test_forecast_mapping_one_sorted_fetch_group():
    payload = forecast_payload(TOLEDO, NOW, periods=40)
    payload["list"].reverse()
    records = make_client(FakeSession(FakeResponse(200, payload)), Clock(NOW)).forecast(TOLEDO)
    assert len(records) == 40
    assert len({r.fetch_id for r in records}) == 1
    assert [r.valid_at_utc for r in records] == sorted(r.valid_at_utc for r in records)
    assert {r.retrieved_at_utc for r in records} == {NOW}
    # 0.3 * 100 must be exactly 30 so a "<= 30 %" preference passes at the boundary.
    assert all(r.precipitation_probability_pct == 30.0 for r in records)
    assert records[0].wind_kmh == pytest.approx(10.8)


def test_missing_or_malformed_metrics_stay_none():
    payload = forecast_payload(TOLEDO, NOW, periods=4)
    del payload["list"][0]["pop"]
    payload["list"][1]["main"] = {"temp": True, "humidity": 150}
    payload["list"][2]["wind"] = {"speed": -1}
    payload["list"][3]["clouds"] = "cloudy"
    first, second, third, fourth = make_client(FakeSession(FakeResponse(200, payload)), Clock(NOW)).forecast(TOLEDO)
    assert first.precipitation_probability_pct is None and first.temperature_c is not None
    assert second.temperature_c is None and second.humidity_pct is None
    assert third.wind_kmh is None
    assert fourth.cloud_pct is None


@pytest.mark.parametrize(
    "change",
    [
        lambda p: p["list"].clear(),
        lambda p: p["list"][0].pop("dt"),
        lambda p: p["list"].append(dict(p["list"][0])),
        lambda p: p.pop("city"),
        lambda p: p["city"].update(country="FR"),
        lambda p: p["city"].update(name="Talavera de la Reina"),
        lambda p: p["city"].update(coord={"lat": 40.1, "lon": -4.0}),
        lambda p: p["city"].update(id=0),
    ],
    ids=["empty", "no-time", "duplicate-time", "no-city", "not-spain", "other-name", "too-far", "bad-id"],
)
def test_untrustworthy_forecasts_are_invalid_data(change):
    payload = forecast_payload(TOLEDO, NOW, periods=3)
    change(payload)
    error = raised(make_client(FakeSession(FakeResponse(200, payload)), Clock(NOW)).forecast, TOLEDO)
    assert isinstance(error, InvalidDataError) and error.message.startswith("Toledo:")


def test_approved_alias_and_expected_id_rules():
    client = make_client(FakeSession())
    alias = current_payload(VITORIA, NOW, name="Vitoria-Gasteiz")
    assert client.map_current(VITORIA, alias, NOW).provider_city_name == "Vitoria-Gasteiz"
    wrong_lugo = current_payload(LUGO, NOW, provider_id=6362983)
    assert raised(client.map_current, LUGO, wrong_lugo, NOW).code == "invalid_data"
    assert client.map_current(LUGO, current_payload(LUGO, NOW, provider_id=3117814), NOW)


def test_all_retained_genuine_responses_map_cleanly():
    """Read-only replay of the 168 genuine P2.3 responses; nothing is written."""
    client = make_client(FakeSession())
    current = forecast_periods = 0
    for line in GENUINE_FETCHES.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        destination = CATALOG[row["city_id"]]
        retrieved = datetime.fromisoformat(row["retrieved_at_utc"])
        if row["kind"] == "current":
            record = client.map_current(destination, row["payload"], retrieved)
            assert record.precipitation_probability_pct is None
            current += 1
        else:
            records = client.map_forecast(destination, row["payload"], retrieved)
            assert all(r.precipitation_probability_pct is not None for r in records)
            forecast_periods += len(records)
    assert (current, forecast_periods) == (84, 3360)
    assert client.request_count == 0


def test_genuine_toledo_values_convert_as_documented():
    row = json.loads(GENUINE_FETCHES.read_text(encoding="utf-8").splitlines()[0])
    assert row["city_id"] == TOLEDO.city_id and row["kind"] == "current"
    record = make_client(FakeSession()).map_current(
        TOLEDO, row["payload"], datetime.fromisoformat(row["retrieved_at_utc"])
    )
    payload = row["payload"]
    assert record.temperature_c == payload["main"]["temp"]
    assert record.wind_kmh == pytest.approx(payload["wind"]["speed"] * 3.6)
    assert record.valid_at_utc == datetime.fromtimestamp(payload["dt"], UTC)
    assert record.retrieved_at_utc != record.valid_at_utc
