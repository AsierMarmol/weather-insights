"""P3.2 reusable JSON API base class and the OpenWeatherMap provider client.

``JSONAPIClient`` knows how to call *any* key-authenticated JSON API: it paces
requests, applies timeouts without following redirects, turns HTTP statuses
into distinct safe errors, retries one transient failure and checks that the
body is a JSON object. ``OpenWeatherClient`` adds only what is specific to
OpenWeatherMap: endpoints, request parameters, location checks and the field
mapping into ``WeatherRecord`` objects (see WEATHER_API_CONTRACT.md).

Error messages never contain the API key, request URLs, raw request exceptions
or provider error bodies. Every error is raised ``from None`` so the original
exception (whose text can include the full URL with the key) is not chained.
Clients only fetch and map; ``service.WeatherService`` owns saving and caching.
"""

from __future__ import annotations

import math
import threading
import time
import unicodedata
from collections import deque
from collections.abc import Callable, Mapping
from datetime import datetime, timezone

import requests

from weather_app.config import get_api_key, load_location_overrides
from weather_app.models import Destination, WeatherRecord

# --- errors


class APIError(Exception):
    """A safe, user-presentable API failure with a stable error ``code``."""

    code = "provider"
    transient = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class InvalidInputError(APIError, ValueError):
    """The request was rejected before (or by) the provider as invalid input.
    """

    code = "invalid_input"


class AuthenticationError(APIError):
    """The API key is missing, invalid, inactive or not authorized."""

    code = "authentication"


class LocationNotFoundError(APIError):
    """The provider does not know the requested location."""

    code = "location_not_found"


class RateLimitError(APIError):
    """The provider's request quota was exceeded."""

    code = "rate_limited"


class NetworkError(APIError):
    """No usable answer arrived: timeout or connection failure."""

    code = "network"
    transient = True


class ProviderError(APIError):
    """The provider answered with an unexpected or server-side error status."""

    code = "provider"

    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


class InvalidDataError(APIError):
    """The response was received but cannot be trusted as the requested data.
    """

    code = "invalid_data"


# --- request pacing


class RateLimiter:
    """Sliding-window cap shared by every request, including failures and
    retries.

    ``wait()`` blocks until another call fits in the window. Holding the
    lock
    while sleeping makes concurrent callers queue in order.
    """

    def __init__(
        self,
        max_calls: int = 40,
        period_s: float = 60.0,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if (
            isinstance(max_calls, bool)
            or not isinstance(max_calls, int)
            or max_calls < 1
        ):
            raise ValueError("max_calls must be a positive whole number")
        if not period_s > 0:
            raise ValueError("period_s must be positive")
        self.max_calls = max_calls
        self.period_s = float(period_s)
        self._clock = clock
        self._sleep = sleep
        self._calls: deque[float] = deque()
        self._lock = threading.Lock()

    def wait(self) -> float:
        """Reserve one call slot and return how many seconds were spent
        waiting.
        """
        with self._lock:
            waited = 0.0
            now = self._clock()
            self._discard_before(now)
            if len(self._calls) >= self.max_calls:
                delay = self._calls[0] + self.period_s - now
                if delay > 0:
                    self._sleep(delay)
                    waited = delay
                now = self._clock()
                self._discard_before(now)
            self._calls.append(now)
            return waited

    def _discard_before(self, now: float) -> None:
        while self._calls and self._calls[0] <= now - self.period_s:
            self._calls.popleft()


# One queue for the whole process (WEATHER_API_CONTRACT.md: 40 calls/minute).
OPENWEATHER_RATE_LIMITER = RateLimiter(max_calls=40, period_s=60.0)


# --- generic JSON API base


class JSONAPIClient:
    """Reusable base for JSON APIs that authenticate with a key query
    parameter.

    Public: ``base_url`` and ``request_count`` for callers and tests.
    Protected: ``_get_json`` and ``_error_for_status`` for provider
    subclasses.
    Private: the credential and its parameter name, name-mangled so a
    subclass
    cannot accidentally overwrite or log them.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str,
        api_key_parameter: str,
        session: requests.Session | None = None,
        rate_limiter: RateLimiter | None = None,
        timeout: tuple[float, float] = (5.0, 20.0),
        max_retries: int = 1,
        retry_delay_s: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.startswith(
            "https://"
        ):
            raise ValueError("base_url must be an https:// URL")
        if not isinstance(api_key, str) or not api_key.strip():
            raise AuthenticationError("No API key was provided.")
        if (
            not isinstance(api_key_parameter, str)
            or not api_key_parameter.strip()
        ):
            raise ValueError("api_key_parameter must be non-empty text")
        if (
            isinstance(max_retries, bool)
            or not isinstance(max_retries, int)
            or max_retries < 0
        ):
            raise ValueError("max_retries must be a non-negative whole number")
        self.base_url = base_url.rstrip("/")
        self.__api_key = api_key.strip()
        self.__api_key_parameter = api_key_parameter
        self.__owns_session = session is None
        self._session = session if session is not None else requests.Session()
        self._rate_limiter = (
            rate_limiter if rate_limiter is not None else RateLimiter()
        )
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay_s = retry_delay_s
        self._sleep = sleep
        self._request_count = 0

    @property
    def request_count(self) -> int:
        """HTTP attempts sent by this client, including failed ones and
        retries.
        """
        return self._request_count

    def __repr__(self) -> str:
        # The key is deliberately masked so logging a client never leaks it.
        return (
            f"{type(self).__name__}(base_url={self.base_url!r}, api_key='***')"
        )

    def __enter__(self) -> JSONAPIClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP session if this client created it."""
        if self.__owns_session:
            self._session.close()

    def _get_json(self, path: str, params: Mapping[str, object]) -> dict:
        """GET ``base_url/path`` with ``params`` and return the JSON object.

        Validates the request first, then makes at most ``1 + max_retries``
        paced attempts; only transient failures (network or 5xx) are retried.
        """
        if (
            not isinstance(path, str)
            or not path
            or path.startswith("/")
            or "://" in path
        ):
            raise InvalidInputError(
                "The request path must be a relative endpoint name."
            )
        if not isinstance(params, Mapping) or not all(
            isinstance(k, str) for k in params
        ):
            raise InvalidInputError(
                "Request parameters must be a mapping with text names."
            )
        if self.__api_key_parameter in params:
            raise InvalidInputError(
                "Request parameters must not supply the API key."
            )
        attempt = 0
        while True:
            try:
                return self.__request_once(path, params)
            except APIError as error:
                if not error.transient or attempt >= self._max_retries:
                    raise
                attempt += 1
                self._sleep(self._retry_delay_s)

    def __request_once(self, path: str, params: Mapping[str, object]) -> dict:
        self._rate_limiter.wait()
        self._request_count += 1
        query = {**params, self.__api_key_parameter: self.__api_key}
        try:
            response = self._session.get(
                f"{self.base_url}/{path}",
                params=query,
                timeout=self._timeout,
                allow_redirects=False,
            )
        except requests.Timeout:
            raise NetworkError(
                "The weather service did not respond in time."
            ) from None
        except requests.ConnectionError:
            raise NetworkError(
                "Could not connect to the weather service. Check your internet"
                " connection."
            ) from None
        except requests.RequestException:
            raise NetworkError(
                "The weather request could not be completed."
            ) from None
        if response.status_code != 200:
            raise self._error_for_status(response.status_code)
        try:
            payload = response.json()
        except ValueError:
            raise InvalidDataError(
                "The weather service returned a response that is not JSON."
            ) from None
        if not isinstance(payload, dict):
            raise InvalidDataError(
                "The weather service returned an unexpected response shape."
            )
        return payload

    def _error_for_status(self, status: int) -> APIError:
        """Translate a non-200 status into a distinct safe error (subclasses
        may refine).
        """
        if status in (401, 403):
            return AuthenticationError(
                "The API key was rejected (invalid, inactive or not"
                " authorized). Check OPENWEATHER_API_KEY in your local"
                " variables.env."
            )
        if status == 404:
            return LocationNotFoundError(
                "The provider could not find the requested location."
            )
        if status == 429:
            return RateLimitError(
                "The provider's request limit was reached. Wait a minute and"
                " try again."
            )
        if status == 400:
            return InvalidInputError(
                "The provider rejected the request parameters."
            )
        if 300 <= status < 400:
            return ProviderError(
                "The provider answered with a redirect, which was not"
                " followed."
            )
        if status >= 500:
            return ProviderError(
                f"The weather service had a server error (HTTP {status}). Try"
                " again later.",
                transient=True,
            )
        return ProviderError(
            "The weather service answered with unexpected HTTP status"
            f" {status}."
        )


# --- OpenWeatherMap provider


def _name_key(value: str) -> str:
    """Compare names ignoring accents, punctuation and case (no invented
    aliases).
    """
    plain = unicodedata.normalize("NFKD", value)
    return "".join(
        c
        for c in plain.casefold()
        if c.isalnum() and not unicodedata.combining(c)
    )


def _finite(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = phi2 - phi1, math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 6371.0088 * 2 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def _metric(
    container: object,
    name: str,
    *,
    scale: float = 1.0,
    low: float | None = None,
    high: float | None = None,
) -> float | None:
    """Read one measurement; absent, malformed or out-of-range values become
    None.
    """
    if not isinstance(container, dict):
        return None
    value = container.get(name)
    if not _finite(value):
        return None
    if (low is not None and value < low) or (
        high is not None and value > high
    ):
        return None
    if scale == 1.0:
        return float(value)
    # Remove binary noise from the unit conversion (0.3 * 100 is
    # 30.000000000000004
    # in floating point, which would wrongly fail a "<= 30 %" preference).
    # Provider
    # values carry at most two decimals, so nine decimals lose no information.
    return round(float(value) * scale, 9)


class OpenWeatherClient(JSONAPIClient):
    """OpenWeatherMap current conditions and 5-day/3-hour forecast for catalog
    destinations.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    UNITS = "metric"
    LANGUAGE = "en"
    COUNTRY = "ES"
    # Same plausibility tolerance the P2.3 access verification used.
    MAX_LOCATION_DISTANCE_KM = 10.0

    def __init__(
        self,
        api_key: str,
        *,
        session: requests.Session | None = None,
        overrides: Mapping[str, dict] | None = None,
        rate_limiter: RateLimiter | None = None,
        clock: Callable[[], datetime] | None = None,
        **options,
    ) -> None:
        super().__init__(
            self.BASE_URL,
            api_key=api_key,
            api_key_parameter="appid",
            session=session,
            rate_limiter=(
                rate_limiter
                if rate_limiter is not None
                else OPENWEATHER_RATE_LIMITER
            ),
            **options,
        )
        self._overrides = dict(
            load_location_overrides() if overrides is None else overrides
        )
        self._clock = (
            clock
            if clock is not None
            else (lambda: datetime.now(timezone.utc))
        )

    @classmethod
    def from_environment(cls, **kwargs) -> OpenWeatherClient:
        """Build a client with the local key; a missing key is an
        authentication error.
        """
        try:
            key = get_api_key()
        except ValueError as error:
            raise AuthenticationError(str(error)) from None
        return cls(key, **kwargs)

    # -- requests

    def request_parameters(
        self, destination: Destination
    ) -> dict[str, object]:
        """The exact provider parameters (without the key) used for a
        destination.

        Catalog coordinates are used unless a documented override requests a
        verified provider city ID (Lugo). The service also uses these
        parameters as part of its cache key.
        """
        self._require_destination(destination)
        override = self._overrides.get(destination.city_id, {})
        if "request_parameters" in override:
            params: dict[str, object] = dict(override["request_parameters"])
        else:
            params = {
                "lat": destination.latitude,
                "lon": destination.longitude,
            }
        params["units"] = self.UNITS
        params["lang"] = self.LANGUAGE
        return params

    def current(self, destination: Destination) -> WeatherRecord:
        """Fetch and map current conditions (one record; precipitation
        probability is None).
        """
        payload = self._get_json(
            "weather", self.request_parameters(destination)
        )
        retrieved_at = self._now()
        return self.map_current(destination, payload, retrieved_at)

    def forecast(self, destination: Destination) -> list[WeatherRecord]:
        """Fetch and map the full 3-hour forecast, ordered by valid time."""
        payload = self._get_json(
            "forecast", self.request_parameters(destination)
        )
        retrieved_at = self._now()
        return self.map_forecast(destination, payload, retrieved_at)

    # -- mapping (also usable for deliberately importing retained raw
    # responses) --

    def map_current(
        self,
        destination: Destination,
        payload: dict,
        retrieved_at: datetime,
        *,
        fetch_id: str | None = None,
    ) -> WeatherRecord:
        """Map a /weather response to a WeatherRecord after checking its
        location.
        """
        self._require_destination(destination)
        if not isinstance(payload, dict):
            raise InvalidDataError(
                f"{destination.city}: the response is not a JSON object."
            )
        system = payload.get("sys")
        country = system.get("country") if isinstance(system, dict) else None
        provider_id, provider_name, lat, lon = self._check_location(
            destination, payload, country
        )
        return self._record(
            destination,
            payload,
            kind="current",
            fetch_id=fetch_id or WeatherRecord.new_fetch_id(),
            retrieved_at=retrieved_at,
            provider=(provider_id, provider_name, lat, lon),
        )

    def map_forecast(
        self,
        destination: Destination,
        payload: dict,
        retrieved_at: datetime,
        *,
        fetch_id: str | None = None,
    ) -> list[WeatherRecord]:
        """Map a /forecast response to one fetch group of WeatherRecords."""
        self._require_destination(destination)
        if not isinstance(payload, dict):
            raise InvalidDataError(
                f"{destination.city}: the response is not a JSON object."
            )
        city = payload.get("city")
        if not isinstance(city, dict):
            raise InvalidDataError(
                f"{destination.city}: the forecast has no location details."
            )
        provider = self._check_location(destination, city, city.get("country"))
        periods = payload.get("list")
        if not isinstance(periods, list) or not periods:
            raise InvalidDataError(
                f"{destination.city}: the forecast contains no periods."
            )
        fetch_id = fetch_id or WeatherRecord.new_fetch_id()
        records = [
            self._record(
                destination,
                period,
                kind="forecast",
                fetch_id=fetch_id,
                retrieved_at=retrieved_at,
                provider=provider,
            )
            for period in periods
        ]
        if len({record.valid_at_utc for record in records}) != len(records):
            raise InvalidDataError(
                f"{destination.city}: the forecast repeats a forecast time."
            )
        return sorted(records)

    # -- protected helpers

    def _now(self) -> datetime:
        return self._clock()

    @staticmethod
    def _require_destination(destination: object) -> None:
        if not isinstance(destination, Destination):
            raise InvalidInputError(
                "A catalog Destination is required for a weather request."
            )

    def _check_location(
        self, destination: Destination, location: dict, country: object
    ) -> tuple[int, str, float, float]:
        """Reject responses that do not plausibly describe the requested
        destination.
        """
        place = destination.city
        provider_id = location.get("id")
        name = location.get("name")
        coord = location.get("coord")
        lat = coord.get("lat") if isinstance(coord, dict) else None
        lon = coord.get("lon") if isinstance(coord, dict) else None
        if (
            isinstance(provider_id, bool)
            or not isinstance(provider_id, int)
            or provider_id <= 0
        ):
            raise InvalidDataError(
                f"{place}: the response has no valid provider location id."
            )
        if not isinstance(name, str) or not name.strip():
            raise InvalidDataError(
                f"{place}: the response has no location name."
            )
        if not (
            _finite(lat)
            and _finite(lon)
            and -90 <= lat <= 90
            and -180 <= lon <= 180
        ):
            raise InvalidDataError(
                f"{place}: the response has no valid coordinates."
            )
        if country != self.COUNTRY:
            raise InvalidDataError(
                f"{place}: the provider returned a location outside Spain."
            )
        override = self._overrides.get(destination.city_id, {})
        expected_id = override.get("expected_provider_id")
        if expected_id is not None and provider_id != expected_id:
            raise InvalidDataError(
                f"{place}: the provider returned a different city id."
            )
        accepted = {_name_key(place)} | {
            _name_key(n) for n in override.get("accepted_names", ())
        }
        if _name_key(name) not in accepted:
            raise InvalidDataError(
                f"{place}: the provider returned {name.strip()!r}, which does"
                " not match this destination."
            )
        distance = _distance_km(
            destination.latitude, destination.longitude, lat, lon
        )
        if distance > self.MAX_LOCATION_DISTANCE_KM:
            raise InvalidDataError(
                f"{place}: the provider location is {distance:.0f} km from the"
                " catalog coordinates."
            )
        return provider_id, name.strip(), float(lat), float(lon)

    def _record(
        self,
        destination: Destination,
        item: object,
        *,
        kind: str,
        fetch_id: str,
        retrieved_at: datetime,
        provider: tuple[int, str, float, float],
    ) -> WeatherRecord:
        if not isinstance(item, dict):
            raise InvalidDataError(
                f"{destination.city}: a {kind} entry is malformed."
            )
        moment = item.get("dt")
        if (
            isinstance(moment, bool)
            or not isinstance(moment, int)
            or moment <= 0
        ):
            raise InvalidDataError(
                f"{destination.city}: a {kind} entry has no valid time."
            )
        provider_id, provider_name, lat, lon = provider
        main, wind = item.get("main"), item.get("wind")
        probability = (
            _metric(item, "pop", scale=100.0, low=0.0, high=1.0)
            if kind == "forecast"
            else None
        )
        try:
            return WeatherRecord(
                fetch_id=fetch_id,
                city_id=destination.city_id,
                kind=kind,
                retrieved_at_utc=retrieved_at,
                valid_at_utc=datetime.fromtimestamp(moment, timezone.utc),
                latitude=lat,
                longitude=lon,
                temperature_c=_metric(main, "temp"),
                wind_kmh=_metric(wind, "speed", scale=3.6, low=0.0),
                precipitation_probability_pct=probability,
                humidity_pct=_metric(main, "humidity", low=0.0, high=100.0),
                cloud_pct=_metric(
                    item.get("clouds"), "all", low=0.0, high=100.0
                ),
                provider_city_id=provider_id,
                provider_city_name=provider_name,
            )
        except (ValueError, OverflowError, OSError):
            raise InvalidDataError(
                f"{destination.city}: a {kind} entry could not be normalized."
            ) from None
