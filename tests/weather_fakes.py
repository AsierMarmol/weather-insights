"""Offline test doubles for P3.2. All weather values here are SYNTHETIC test inputs.

Nothing in this module performs HTTP or writes to data/weather.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from weather_app.client import OpenWeatherClient, RateLimiter
from weather_app.storage import load_destinations

UTC = timezone.utc
DUMMY_KEY = "dummy-test-key-0123456789"
CATALOG = {d.city_id: d for d in load_destinations()}
TOLEDO = CATALOG["ES-45168"]
SEGOVIA = CATALOG["ES-40194"]
LUGO = CATALOG["ES-27028"]
VITORIA = CATALOG["ES-01059"]


class Clock:
    """Controllable aware-UTC clock."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta) -> None:
        self.now += timedelta(**delta)


class FakeResponse:
    def __init__(self, status: int = 200, payload: object = None, *, bad_json: bool = False) -> None:
        self.status_code = status
        self._payload = payload
        self._bad_json = bad_json

    def json(self) -> object:
        if self._bad_json:
            raise requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0)
        return self._payload


class FakeSession:
    """Records every GET and answers from a queue or a handler(url, params)."""

    def __init__(self, *answers, handler=None) -> None:
        self.answers = list(answers)
        self.handler = handler
        self.calls: list[dict] = []

    def get(self, url, *, params, timeout, allow_redirects):
        self.calls.append(
            {"url": url, "params": dict(params), "timeout": timeout, "allow_redirects": allow_redirects}
        )
        answer = self.handler(url, params) if self.handler else self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def close(self) -> None:
        pass


def make_client(session: FakeSession, clock: Clock | None = None, **options) -> OpenWeatherClient:
    options.setdefault("rate_limiter", RateLimiter(max_calls=10_000, period_s=60))
    options.setdefault("sleep", lambda seconds: None)
    return OpenWeatherClient(DUMMY_KEY, session=session, clock=clock, **options)


def location(destination, *, name=None, provider_id=2510409, country="ES", lat=None, lon=None) -> dict:
    return {
        "id": provider_id,
        "name": destination.city if name is None else name,
        "coord": {
            "lat": destination.latitude if lat is None else lat,
            "lon": destination.longitude if lon is None else lon,
        },
        "country": country,
    }


def current_payload(destination, valid_at: datetime, **location_options) -> dict:
    """Synthetic /weather body shaped like OpenWeatherMap's."""
    place = location(destination, **location_options)
    return {
        "coord": place["coord"],
        "main": {"temp": 21.5, "humidity": 40},
        "wind": {"speed": 5.0, "gust": 9.0},
        "clouds": {"all": 20},
        "dt": int(valid_at.timestamp()),
        "sys": {"country": place["country"]},
        "id": place["id"],
        "name": place["name"],
        "cod": 200,
    }


def forecast_payload(destination, first_valid_at: datetime, periods: int = 40, **location_options) -> dict:
    """Synthetic /forecast body with ``periods`` 3-hour entries."""
    items = []
    for index in range(periods):
        moment = first_valid_at + timedelta(hours=3 * index)
        items.append(
            {
                "dt": int(moment.timestamp()),
                "main": {"temp": 18.0 + index % 5, "humidity": 55},
                "wind": {"speed": 3.0},
                "clouds": {"all": 10},
                "pop": 0.3,
            }
        )
    return {"cod": "200", "cnt": periods, "list": items, "city": location(destination, **location_options)}


def catalog_handler(clock: Clock, *, failures: dict | None = None):
    """Answer like the provider for any catalog city; ``failures`` maps city_id -> status."""
    by_coordinates = {(d.latitude, d.longitude): d for d in CATALOG.values()}
    failures = failures or {}

    def handle(url, params):
        if "id" in params:
            destination, provider_id = LUGO, params["id"]
        else:
            destination, provider_id = by_coordinates[(params["lat"], params["lon"])], 1000
        if destination.city_id in failures:
            return FakeResponse(failures[destination.city_id], {"message": "synthetic failure"})
        name = "Vitoria-Gasteiz" if destination is VITORIA else None
        if url.endswith("/weather"):
            return FakeResponse(200, current_payload(destination, clock.now, provider_id=provider_id, name=name))
        start = clock.now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=3)
        return FakeResponse(200, forecast_payload(destination, start, provider_id=provider_id, name=name))

    return handle
