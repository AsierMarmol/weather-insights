"""P3.2 request/save service: the single path from a weather request to saved
records.

``WeatherService`` asks ``OpenWeatherClient`` for data, saves every fresh
successful response once through P3.1's ``WeatherStore`` and only then
caches
and returns it. Cached or already-stored data is reused without HTTP and is
never saved again. Every method returns a plain result dictionary (P2.4)::

    {"records": [WeatherRecord, ...], "from_cache": bool,
     "error": None | {"code": str, "message": str}}

Error codes: invalid_input, authentication, location_not_found,
rate_limited,
network, provider, invalid_data, storage. A failed save is reported as
``storage`` with no records, so unsaved data is never used for analysis; the
fetched batch is kept in memory and saved first on the next successful
write.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta, timezone

from weather_app.client import APIError, InvalidInputError, OpenWeatherClient
from weather_app.models import Destination, WeatherRecord
from weather_app.storage import StorageError, WeatherStore

ProgressCallback = Callable[[int, int, str, dict], None]


def _result(records: Sequence[WeatherRecord], from_cache: bool) -> dict:
    return {"records": list(records), "from_cache": from_cache, "error": None}


def _failure(code: str, message: str) -> dict:
    return {
        "records": [],
        "from_cache": False,
        "error": {"code": code, "message": message},
    }


class WeatherService:
    """Fetch, save once, then cache current conditions and forecasts per
    destination.
    """

    CURRENT_TTL = timedelta(minutes=30)
    FORECAST_TTL = timedelta(hours=3)
    MAX_CURRENT_OBSERVATION_AGE = timedelta(hours=2)
    # Failures that would repeat for every remaining city stop a batch.
    BATCH_STOP_CODES = frozenset({"authentication", "rate_limited", "storage"})

    def __init__(
        self,
        client: OpenWeatherClient,
        store: WeatherStore,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.client = client
        self.store = store
        self._clock = (
            clock
            if clock is not None
            else (lambda: datetime.now(timezone.utc))
        )
        self.__cache: dict[tuple, list[WeatherRecord]] = {}
        self.__unsaved: list[list[WeatherRecord]] = []
        self.__lock = threading.RLock()

    @classmethod
    def from_environment(
        cls, store: WeatherStore | None = None
    ) -> WeatherService:
        """Service using the local API key and the repository's weather CSV.

        Raises ``AuthenticationError`` with setup guidance if no key is
        configured.
        """
        return cls(
            OpenWeatherClient.from_environment(),
            store if store is not None else WeatherStore(),
        )

    @property
    def unsaved_record_count(self) -> int:
        """Fetched records still waiting to be written after a storage failure.
        """
        with self.__lock:
            return sum(len(batch) for batch in self.__unsaved)

    def __repr__(self) -> str:
        return f"WeatherService(client={self.client!r}, store={self.store!r})"

    # -- public requests

    def current(
        self, destination: Destination, *, force_refresh: bool = False
    ) -> dict:
        """Current conditions: fresh for 30 minutes and while the observation
        is under 2 hours old.
        """
        return self._request("current", destination, force_refresh)

    def forecast(
        self, destination: Destination, *, force_refresh: bool = False
    ) -> dict:
        """The full 3-hour forecast, reused for up to 3 hours after retrieval.
        """
        return self._request("forecast", destination, force_refresh)

    def forecast_many(
        self,
        destinations: Sequence[Destination],
        *,
        force_refresh: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> dict[str, dict]:
        """Forecasts for several destinations, keyed by city_id in input order.

        An ordinary failure affects only its own city. Authentication, quota
        and
        storage failures stop further requests; the remaining cities get an
        explicit result with the same code instead of being silently
        dropped.
        ``on_progress(done, total, city_id, result)`` lets the UI show
        progress.
        Raises ``InvalidInputError`` if the input is not a list of
        Destinations.
        """
        if isinstance(destinations, (str, bytes)) or not isinstance(
            destinations, Sequence
        ):
            raise InvalidInputError(
                "Destinations must be a list of catalog Destinations."
            )
        unique: dict[str, Destination] = {}
        for destination in destinations:
            if not isinstance(destination, Destination):
                raise InvalidInputError(
                    "Destinations must be a list of catalog Destinations."
                )
            unique.setdefault(destination.city_id, destination)
        results: dict[str, dict] = {}
        stopped: dict | None = None
        total = len(unique)
        for done, (city_id, destination) in enumerate(unique.items(), 1):
            if stopped is not None:
                result = _failure(
                    stopped["code"],
                    f"{destination.city}: not requested because an earlier"
                    f" request failed ({stopped['code']}).",
                )
            else:
                result = self.forecast(
                    destination, force_refresh=force_refresh
                )
                error = result["error"]
                if (
                    error is not None
                    and error["code"] in self.BATCH_STOP_CODES
                ):
                    stopped = error
            results[city_id] = result
            if on_progress is not None:
                on_progress(done, total, city_id, result)
        return results

    def retry_unsaved(self) -> int:
        """Try again to save batches kept after a storage failure; return
        records still unsaved.
        """
        with self.__lock:
            try:
                self.__flush_unsaved()
            except (StorageError, ValueError):
                pass
            return self.unsaved_record_count

    def clear_cache(self) -> None:
        """Forget in-memory results (stored records are untouched)."""
        with self.__lock:
            self.__cache.clear()

    # -- internals

    def _request(
        self, kind: str, destination: object, force_refresh: object
    ) -> dict:
        if not isinstance(destination, Destination):
            return _failure(
                "invalid_input",
                "A catalog destination is required for a weather request.",
            )
        if not isinstance(force_refresh, bool):
            return _failure(
                "invalid_input", "force_refresh must be True or False."
            )
        place = destination.city
        params = self.client.request_parameters(destination)
        key = (kind, destination.city_id, tuple(sorted(params.items())))

        if not force_refresh:
            try:
                reused = self._reusable(kind, key, destination)
            except StorageError as error:
                return _failure(
                    "storage",
                    f"{place}: saved weather could not be read. {error}",
                )
            if reused:
                return _result(reused, from_cache=True)

        try:
            if kind == "current":
                records = [self.client.current(destination)]
            else:
                records = self.client.forecast(destination)
        except APIError as error:
            return _failure(error.code, f"{place}: {error.message}")

        try:
            self._save(records)
        except StorageError as error:
            return _failure(
                "storage",
                f"{place}: weather was fetched but could not be saved, so it"
                f" is not used yet. {error}",
            )
        except ValueError:
            return _failure(
                "invalid_data",
                f"{place}: the fetched records conflict with saved records.",
            )

        with self.__lock:
            self.__cache[key] = records
        return _result(records, from_cache=False)

    def _reusable(
        self, kind: str, key: tuple, destination: Destination
    ) -> list[WeatherRecord]:
        """Fresh records from memory, else the newest fresh group already in
        the store.
        """
        now = self._clock()
        with self.__lock:
            cached = self.__cache.get(key)
        if cached and self._is_fresh(kind, cached, now):
            return cached
        if kind == "forecast":
            stored = self.store.latest_forecast(destination.city_id)
        else:
            stored = self._latest_current(destination.city_id)
        if stored and self._is_fresh(kind, stored, now):
            with self.__lock:
                self.__cache[key] = stored
            return stored
        return []

    def _latest_current(self, city_id: str) -> list[WeatherRecord]:
        records = self.store.load(city_id=city_id, kind="current")
        if not records:
            return []
        return [max(records, key=lambda record: record.retrieved_at_utc)]

    def _is_fresh(
        self, kind: str, records: Sequence[WeatherRecord], now: datetime
    ) -> bool:
        retrieved_at = records[0].retrieved_at_utc
        age = max(timedelta(0), now - retrieved_at)
        if kind == "forecast":
            return age <= self.FORECAST_TTL
        observation_age = max(timedelta(0), now - records[0].valid_at_utc)
        return (
            age <= self.CURRENT_TTL
            and observation_age <= self.MAX_CURRENT_OBSERVATION_AGE
        )

    def _save(self, records: Sequence[WeatherRecord]) -> None:
        """The single save path: queue the batch, then write everything still
        pending.
        """
        with self.__lock:
            self.__unsaved.append(list(records))
            self.__flush_unsaved()

    def __flush_unsaved(self) -> None:
        while self.__unsaved:
            try:
                self.store.append(self.__unsaved[0])
            except ValueError:
                # A conflicting batch can never be saved; drop it and report
                # it.
                self.__unsaved.pop(0)
                raise
            self.__unsaved.pop(0)
