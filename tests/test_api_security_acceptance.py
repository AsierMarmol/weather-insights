"""P5.2 API/security/save acceptance through the connected app.

Every weather value and failure here is SYNTHETIC. HTTP is answered by
fake sessions and live requests are blocked; saves go to temporary files.
The genuine data directory is checked byte-for-byte after each test.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from streamlit.testing.v1 import AppTest
from weather_fakes import (
    CATALOG,
    DUMMY_KEY,
    LUGO,
    SEGOVIA,
    TOLEDO,
    Clock,
    FakeResponse,
    FakeSession,
    catalog_handler,
    forecast_payload,
    make_client,
)

from weather_app import client as client_module
from weather_app import config, searcher
from weather_app.client import (
    OPENWEATHER_RATE_LIMITER,
    APIError,
    AuthenticationError,
    OpenWeatherClient,
)
from weather_app.service import WeatherService
from weather_app.storage import WeatherStore

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 12, 6, tzinfo=timezone.utc)
SEVILLE = CATALOG["ES-41091"]
PLACES = [TOLEDO, SEGOVIA, SEVILLE]
SECRET_MARKERS = (DUMMY_KEY, "appid", "api.openweathermap.org", "Traceback")


def city_of(params):
    """The catalog city a fake request is for (Lugo is asked for by ID)."""
    if "id" in params:
        return LUGO.city_id
    for destination in CATALOG.values():
        if (destination.latitude, destination.longitude) == (
            params["lat"],
            params["lon"],
        ):
            return destination.city_id
    raise AssertionError(f"Unexpected request parameters: {params}")


class Scripted:
    """Answer each listed city from its queue, then like the provider."""

    def __init__(self, clock, **queues):
        self.normal = catalog_handler(clock)
        self.queues = {CITY[name]: list(answers) for name, answers in
                       queues.items()}

    def __call__(self, url, params):
        queue = self.queues.get(city_of(params))
        return queue.pop(0) if queue else self.normal(url, params)


CITY = {"toledo": TOLEDO.city_id, "segovia": SEGOVIA.city_id,
        "seville": SEVILLE.city_id}


def calls_for(session, destination):
    return [c for c in session.calls if city_of(c["params"]) ==
            destination.city_id]


@pytest.fixture
def genuine_data_unchanged():
    data = {
        p: p.read_bytes() for p in (ROOT / "data").rglob("*") if p.is_file()
    }
    yield
    assert all(p.read_bytes() == contents for p, contents in data.items())


@pytest.fixture
def no_live_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("No live HTTP in acceptance tests")

    monkeypatch.setattr(requests.Session, "request", blocked)


@pytest.fixture
def app_journey(monkeypatch, tmp_path, no_live_http, genuine_data_unchanged):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "weather.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    monkeypatch.setattr(searcher, "utc_now", clock)
    monkeypatch.setattr(searcher, "load_destinations", lambda: PLACES)
    monkeypatch.setattr(
        WeatherService, "from_environment", Mock(return_value=service)
    )
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    return app, service, session, clock


def search(app):
    app.run().button(key="run_search").click().run()
    assert not app.exception


def page_text(app):
    """Everything a user can read on the page, including table cells."""
    parts = [
        str(element.value)
        for kind in ("error", "warning", "info", "success", "markdown",
                     "caption", "text")
        for element in app.get(kind)
    ]
    parts += [frame.value.to_csv() for frame in app.dataframe]
    return "\n".join(parts)


def assert_no_secret(app):
    text = page_text(app)
    for marker in SECRET_MARKERS:
        assert marker not in text


# -- credentials


@pytest.fixture
def key_file(monkeypatch, tmp_path):
    """A private, temporary variables.env; the real one is never read."""
    path = tmp_path / "variables.env"
    monkeypatch.setattr(config, "ENV_FILE", path)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    return path


@pytest.mark.parametrize(
    "contents",
    [
        b"OPENWEATHER_API_KEY=abc123\n",
        b"OPENWEATHER_API_KEY=abc123\r\n",
        b"\xef\xbb\xbfOPENWEATHER_API_KEY=abc123\r\n",
        b'OPENWEATHER_API_KEY="abc123"\n',
        b"export OPENWEATHER_API_KEY=abc123\n",
        b"OPENWEATHER_API_KEY = abc123  # my key\n",
    ],
    ids=["unix", "windows", "bom", "quoted", "export", "comment"],
)
def test_key_file_written_on_macos_or_windows_is_read(key_file, contents):
    key_file.write_bytes(contents)
    assert config.get_api_key() == "abc123"


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le"])
def test_key_file_in_another_encoding_explains_the_fix(key_file, encoding):
    # Windows PowerShell 5 "echo ... > variables.env" writes UTF-16.
    key_file.write_bytes("OPENWEATHER_API_KEY=abc123\n".encode(encoding))
    with pytest.raises(ValueError, match="UTF-8") as raised:
        config.get_api_key()
    assert not isinstance(raised.value, UnicodeDecodeError)
    assert "abc123" not in str(raised.value)
    with pytest.raises(AuthenticationError, match="UTF-8"):
        OpenWeatherClient.from_environment()


def test_shell_key_still_works_when_the_file_is_unreadable(
    key_file, monkeypatch
):
    key_file.write_bytes("OPENWEATHER_API_KEY=x\n".encode("utf-16"))
    monkeypatch.setenv("OPENWEATHER_API_KEY", "from-shell")
    assert config.get_api_key() == "from-shell"


def test_app_shows_how_to_fix_a_key_file_in_another_encoding(
    key_file, monkeypatch, no_live_http, genuine_data_unchanged
):
    key_file.write_bytes("OPENWEATHER_API_KEY=abc123\n".encode("utf-16"))
    monkeypatch.setattr(searcher, "load_destinations", lambda: PLACES)
    monkeypatch.setattr(searcher, "utc_now", Clock(NOW))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    search(app)
    assert app.error[0].value == searcher.MESSAGES["authentication"]
    assert any("UTF-8" in c.value for c in app.caption)
    assert "abc123" not in page_text(app)


def test_environment_variable_takes_precedence_over_the_file(
    key_file, monkeypatch
):
    key_file.write_text("OPENWEATHER_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "from-shell")
    assert config.get_api_key() == "from-shell"


@pytest.mark.parametrize("contents", ["", "OPENWEATHER_API_KEY=\n",
                                      "OPENWEATHER_API_KEY=   \n"])
def test_missing_key_explains_setup_without_any_request(
    key_file, contents, monkeypatch, no_live_http, genuine_data_unchanged
):
    if contents:
        key_file.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(searcher, "load_destinations", lambda: PLACES)
    monkeypatch.setattr(searcher, "utc_now", Clock(NOW))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    search(app)
    assert "API key" in app.error[0].value
    assert any("variables.env.example" in c.value for c in app.caption)
    assert "weather_service" not in app.session_state
    assert "search_analysis_rows" not in app.session_state
    assert_no_secret(app)


def test_rejected_key_stops_the_batch_and_saves_nothing(app_journey):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, toledo=[FakeResponse(401, {
        "cod": 401, "message": f"Invalid API key {DUMMY_KEY}"})])
    search(app)
    assert len(session.calls) == 1
    assert set(app.session_state.search_errors.values()) == {
        "authentication"
    }
    warnings = [w.value for w in app.warning]
    assert warnings.count(searcher.MESSAGES["authentication"]) == 1
    assert service.store.load() == []
    assert_no_secret(app)


def test_key_is_sent_only_as_a_parameter_over_https(app_journey):
    app, _, session, _ = app_journey
    search(app)
    assert session.calls
    for call in session.calls:
        assert call["url"].startswith("https://api.openweathermap.org/")
        assert DUMMY_KEY not in call["url"]
        assert call["params"]["appid"] == DUMMY_KEY
        assert call["allow_redirects"] is False
        assert call["timeout"] == (5.0, 20.0)


def test_redirect_is_not_followed_and_is_a_provider_failure(app_journey):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, segovia=[FakeResponse(302)])
    search(app)
    assert app.session_state.search_errors == {SEGOVIA.city_id: "provider"}
    assert len(calls_for(session, SEGOVIA)) == 1
    assert len(service.store.load()) == 80


# -- location, network, server and quota failures


@pytest.mark.parametrize(
    "location",
    [
        {"lat": 41.95, "lon": -3.6},  # about 50 km from Segovia
        {"country": "PT"},
        {"name": "Salamanca"},
        {"provider_id": 0},
    ],
    ids=["too-far", "country", "name", "provider-id"],
)
def test_wrong_location_is_rejected_and_other_cities_continue(
    app_journey, location
):
    app, service, session, clock = app_journey
    start = NOW + timedelta(hours=3)
    session.handler = Scripted(
        clock,
        segovia=[FakeResponse(200, forecast_payload(SEGOVIA, start,
                                                    **location))],
    )
    search(app)
    assert app.session_state.search_errors == {
        SEGOVIA.city_id: "invalid_data"
    }
    saved = service.store.load()
    assert len(saved) == 80
    assert SEGOVIA.city_id not in {r.city_id for r in saved}
    assert searcher.MESSAGES["invalid_data"] in [w.value for w in app.warning]


def test_unknown_location_is_reported_without_retry(app_journey):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, seville=[FakeResponse(404)])
    search(app)
    assert app.session_state.search_errors == {
        SEVILLE.city_id: "location_not_found"
    }
    assert len(calls_for(session, SEVILLE)) == 1
    assert len(service.store.load()) == 80


def test_network_failures_retry_once_then_fail_without_details(app_journey):
    app, service, session, clock = app_journey
    leak = requests.exceptions.ConnectionError(
        f"https://api.openweathermap.org/data/2.5/forecast?appid={DUMMY_KEY}"
    )
    session.handler = Scripted(
        clock,
        toledo=[leak, leak],
        segovia=[requests.exceptions.Timeout("read timed out")],
    )
    search(app)
    assert len(calls_for(session, TOLEDO)) == 2
    assert len(calls_for(session, SEGOVIA)) == 2
    assert app.session_state.search_errors == {TOLEDO.city_id: "network"}
    assert len(service.store.load()) == 80
    assert searcher.MESSAGES["network"] in [w.value for w in app.warning]
    assert_no_secret(app)


@pytest.mark.parametrize(
    ("answers", "code", "attempts"),
    [
        ([FakeResponse(503)], None, 2),
        ([FakeResponse(500), FakeResponse(502)], "provider", 2),
        ([FakeResponse(400)], "invalid_input", 1),
        ([FakeResponse(418)], "provider", 1),
    ],
    ids=["5xx-recovers", "5xx-twice", "400", "unexpected"],
)
def test_server_errors_retry_only_when_transient(
    app_journey, answers, code, attempts
):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, toledo=answers)
    search(app)
    assert len(calls_for(session, TOLEDO)) == attempts
    expected = {} if code is None else {TOLEDO.city_id: code}
    assert app.session_state.search_errors == expected
    assert len(service.store.load()) == (120 if code is None else 80)


def test_quota_stops_the_batch_and_next_search_fetches_only_missing(
    app_journey,
):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, segovia=[FakeResponse(429)])
    search(app)
    assert [city_of(c["params"]) for c in session.calls] == [
        TOLEDO.city_id,
        SEGOVIA.city_id,
    ]
    assert app.session_state.search_errors == {
        SEGOVIA.city_id: "rate_limited",
        SEVILLE.city_id: "rate_limited",
    }
    assert len(service.store.load()) == 40
    assert searcher.MESSAGES["rate_limited"] in [w.value for w in app.warning]

    clock.advance(minutes=1)
    app.button(key="run_search").click().run()
    assert [city_of(c["params"]) for c in session.calls[2:]] == [
        SEGOVIA.city_id,
        SEVILLE.city_id,
    ]
    assert app.session_state.search_errors == {}
    assert len(service.store.load()) == 120


def test_one_process_wide_limiter_paces_every_app_session():
    first = OpenWeatherClient("key-one")
    second = OpenWeatherClient("key-two")
    try:
        assert first._rate_limiter is second._rate_limiter
        assert first._rate_limiter is OPENWEATHER_RATE_LIMITER
        assert OPENWEATHER_RATE_LIMITER.max_calls <= 40
        assert OPENWEATHER_RATE_LIMITER.period_s >= 60
    finally:
        first.close()
        second.close()


# -- malformed responses


def _payload(**changes):
    body = forecast_payload(TOLEDO, NOW + timedelta(hours=3))
    for key, value in changes.items():
        if value is KeyError:
            body.pop(key)
        else:
            body[key] = value
    return body


def _duplicate_periods():
    body = _payload()
    body["list"][1]["dt"] = body["list"][0]["dt"]
    return body


def _missing_time():
    body = _payload()
    del body["list"][3]["dt"]
    return body


@pytest.mark.parametrize(
    "response",
    [
        FakeResponse(200, bad_json=True),
        FakeResponse(200, [1, 2, 3]),
        FakeResponse(200, "ok"),
        FakeResponse(200, _payload(list=KeyError)),
        FakeResponse(200, _payload(list=[])),
        FakeResponse(200, _payload(list="none")),
        FakeResponse(200, _payload(city=KeyError)),
        FakeResponse(200, _duplicate_periods()),
        FakeResponse(200, _missing_time()),
    ],
    ids=["not-json", "list", "text", "no-periods", "empty", "bad-periods",
         "no-city", "duplicate-time", "missing-time"],
)
def test_malformed_forecast_is_invalid_data_and_never_saved(
    app_journey, response
):
    app, service, session, clock = app_journey
    session.handler = Scripted(clock, toledo=[response])
    search(app)
    assert app.session_state.search_errors == {TOLEDO.city_id: "invalid_data"}
    assert TOLEDO.city_id not in {r.city_id for r in service.store.load()}
    assert len(calls_for(session, TOLEDO)) == 1
    assert_no_secret(app)


def test_malformed_metrics_are_saved_blank_never_as_zero(app_journey):
    app, service, session, clock = app_journey
    body = _payload()
    body["list"][0]["main"]["temp"] = "hot"
    body["list"][1]["main"]["temp"] = float("nan")
    del body["list"][2]["pop"]
    body["list"][3]["wind"]["speed"] = -4
    session.handler = Scripted(clock, toledo=[FakeResponse(200, body)])
    search(app)
    saved = sorted(
        (r for r in service.store.load() if r.city_id == TOLEDO.city_id),
        key=lambda r: r.valid_at_utc,
    )
    assert len(saved) == 40
    assert saved[0].temperature_c is None
    assert saved[1].temperature_c is None
    assert saved[2].precipitation_probability_pct is None
    assert saved[3].wind_kmh is None
    assert saved[4].temperature_c is not None


# -- saving and reuse


def test_fresh_forecasts_save_once_with_times_and_are_reused(app_journey):
    app, service, session, clock = app_journey
    search(app)
    saved = service.store.load()
    assert len(session.calls) == 3 and len(saved) == 120
    assert {r.retrieved_at_utc for r in saved} == {NOW}
    assert all(r.valid_at_utc > r.retrieved_at_utc for r in saved)
    assert len({r.fetch_id for r in saved}) == 3

    clock.advance(hours=3)  # equal to the forecast TTL: still fresh
    app.button(key="run_search").click().run()
    assert len(session.calls) == 3 and len(service.store.load()) == 120
    assert app.session_state.search_cached_count == 3

    clock.advance(minutes=1)
    app.button(key="run_search").click().run()
    saved = service.store.load()
    assert len(session.calls) == 6 and len(saved) == 240
    assert len({r.fetch_id for r in saved}) == 6


def test_new_service_reuses_saved_forecasts_after_restart(
    tmp_path, no_live_http, genuine_data_unchanged
):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    path = tmp_path / "weather.csv"
    first = WeatherService(make_client(session, clock), WeatherStore(path),
                           clock=clock)
    first.forecast_many(PLACES)
    clock.advance(hours=1)
    second = WeatherService(make_client(session, clock), WeatherStore(path),
                            clock=clock)
    results = second.forecast_many(PLACES)
    assert all(r["from_cache"] and r["error"] is None
               for r in results.values())
    assert len(session.calls) == 3
    assert len(WeatherStore(path).load()) == 120


# -- messages


def test_every_error_code_has_a_fixed_safe_message():
    codes = {
        cls.code
        for cls in vars(client_module).values()
        if isinstance(cls, type) and issubclass(cls, APIError)
    } | WeatherService.BATCH_STOP_CODES
    assert codes <= set(searcher.MESSAGES)
    for code in codes:
        message = searcher.MESSAGES[code]
        assert message and "{" not in message
        for marker in SECRET_MARKERS:
            assert marker not in message


def test_api_errors_never_echo_provider_text():
    session = FakeSession(
        FakeResponse(401, {"message": f"bad key {DUMMY_KEY}"}),
        FakeResponse(500, {"message": "internal path /srv/app"}),
        FakeResponse(500, {"message": "internal path /srv/app"}),
    )
    weather = make_client(session)
    for _ in range(2):
        with pytest.raises(APIError) as raised:
            weather.forecast(TOLEDO)
        text = f"{raised.value} {raised.value.as_dict()} {raised.value!r}"
        assert DUMMY_KEY not in text and "/srv/app" not in text
        assert raised.value.__cause__ is None
    assert DUMMY_KEY not in repr(weather)
