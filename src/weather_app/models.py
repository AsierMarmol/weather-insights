"""P3.1 domain models shared by storage, the API service, analytics and the UI.

The shapes follow the P2.4 shared specification in PHASE2_SCOPE.md. Every model
is an immutable, keyword-only dataclass that validates itself on construction,
so invalid catalog rows, preferences or weather values are rejected before they
reach storage or analytics. Missing weather readings stay ``None``, never zero.
"""

from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass, fields
from datetime import datetime, timedelta, timezone

SCHEMA_VERSION = 1

ACTIVITIES = (
    "Coast",
    "Nature",
    "History and heritage",
    "Food and gastronomy",
    "Urban experiences",
)
DESTINATION_SIZES = ("Large city", "Medium city", "Small city or town")
WEATHER_KINDS = ("current", "forecast")
SUPPORTED_FORECAST_DAYS = (1, 2, 3, 4, 5)

# Exact column order of data/weather/weather_records.csv (P2.4).
RECORD_FIELDS = (
    "schema_version",
    "fetch_id",
    "city_id",
    "kind",
    "retrieved_at_utc",
    "valid_at_utc",
    "latitude",
    "longitude",
    "temperature_c",
    "wind_kmh",
    "precipitation_probability_pct",
    "humidity_pct",
    "cloud_pct",
    "provider_city_id",
    "provider_city_name",
)
_TIME_FIELDS = ("retrieved_at_utc", "valid_at_utc")
_FLOAT_FIELDS = (
    "latitude",
    "longitude",
    "temperature_c",
    "wind_kmh",
    "precipitation_probability_pct",
    "humidity_pct",
    "cloud_pct",
)
_OPTIONAL_METRICS = _FLOAT_FIELDS[2:]

_CITY_ID = re.compile(r"ES-\d{5}")


# --- shared validation helpers -------------------------------------------------


def _number(name: str, value: object, *, optional: bool = False) -> float | None:
    """Return a finite float, rejecting booleans, text and NaN/infinity."""
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _in_range(name: str, value: float | None, low: float, high: float) -> None:
    if value is not None and not low <= value <= high:
        raise ValueError(f"{name} must be between {low:g} and {high:g}")


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _city_id(value: object) -> str:
    text = _text("city_id", value)
    if not _CITY_ID.fullmatch(text):
        raise ValueError("city_id must look like ES- plus five digits")
    return text


def _utc(name: str, value: object) -> datetime:
    """Require a timezone-aware datetime and normalize it to UTC."""
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _choices(name: str, values: object, allowed: tuple[str, ...]) -> tuple[str, ...]:
    """Normalize a selection to a duplicate-free tuple of allowed labels."""
    if isinstance(values, str) or not isinstance(values, (tuple, list)):
        raise ValueError(f"{name} must be a tuple or list of labels")
    chosen: list[str] = []
    for value in values:
        if value not in allowed:
            raise ValueError(f"{name} contains unknown value {value!r}")
        if value in chosen:
            raise ValueError(f"{name} contains {value!r} more than once")
        chosen.append(value)
    return tuple(chosen)


def _set(instance: object, name: str, value: object) -> None:
    # Frozen dataclasses normalize their own fields during __post_init__ this way.
    object.__setattr__(instance, name, value)


def format_utc(value: datetime) -> str:
    """Serialize an aware datetime as an ISO 8601 UTC string."""
    return _utc("timestamp", value).isoformat()


def parse_utc(name: str, text: str) -> datetime:
    """Parse an ISO 8601 timestamp that must carry a UTC offset."""
    try:
        parsed = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        raise ValueError(f"{name} is not an ISO 8601 timestamp") from None
    return _utc(name, parsed)


# --- models -------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Destination:
    """One row of the nine-column destination catalog."""

    city_id: str
    city: str
    region: str
    car_distance_km: float
    car_duration_min: float
    latitude: float
    longitude: float
    activities: tuple[str, ...]
    destination_size: str

    def __post_init__(self) -> None:
        _set(self, "city_id", _city_id(self.city_id))
        _set(self, "city", _text("city", self.city))
        _set(self, "region", _text("region", self.region))
        for name in ("car_distance_km", "car_duration_min"):
            value = _number(name, getattr(self, name))
            if value < 0:
                raise ValueError(f"{name} must not be negative")
            _set(self, name, value)
        _set(self, "latitude", _number("latitude", self.latitude))
        _set(self, "longitude", _number("longitude", self.longitude))
        _in_range("latitude", self.latitude, -90, 90)
        _in_range("longitude", self.longitude, -180, 180)
        activities = _choices("activities", self.activities, ACTIVITIES)
        if not activities:
            raise ValueError("activities must contain at least one tag")
        _set(self, "activities", activities)
        if self.destination_size not in DESTINATION_SIZES:
            raise ValueError(f"unknown destination_size {self.destination_size!r}")

    @property
    def drive_hours(self) -> float:
        """One-way modeled driving time from Madrid, in hours (unrounded)."""
        return self.car_duration_min / 60

    def as_catalog_row(self) -> dict:
        """Plain dictionary for UI tables; activities become a list."""
        row = {f.name: getattr(self, f.name) for f in fields(self)}
        row["activities"] = list(self.activities)
        return row

    def __str__(self) -> str:
        return f"{self.city} ({self.region})"

    def __repr__(self) -> str:
        return (
            f"Destination(city_id={self.city_id!r}, city={self.city!r}, "
            f"region={self.region!r}, drive_hours={self.drive_hours:.2f})"
        )


@dataclass(frozen=True, kw_only=True)
class SearchPreferences:
    """User search settings; empty activity/size tuples mean All."""

    days: int
    temperature_min_c: float
    temperature_max_c: float
    max_precipitation_probability_pct: float
    max_wind_kmh: float
    activities: tuple[str, ...] = ()
    destination_sizes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.days, bool) or self.days not in SUPPORTED_FORECAST_DAYS:
            raise ValueError("days must be a whole number from 1 to 5")
        _set(self, "days", int(self.days))
        low = _number("temperature_min_c", self.temperature_min_c)
        high = _number("temperature_max_c", self.temperature_max_c)
        if low > high:
            raise ValueError("temperature_min_c must not exceed temperature_max_c")
        rain = _number(
            "max_precipitation_probability_pct", self.max_precipitation_probability_pct
        )
        _in_range("max_precipitation_probability_pct", rain, 0, 100)
        wind = _number("max_wind_kmh", self.max_wind_kmh)
        if wind < 0:
            raise ValueError("max_wind_kmh must not be negative")
        _set(self, "temperature_min_c", low)
        _set(self, "temperature_max_c", high)
        _set(self, "max_precipitation_probability_pct", rain)
        _set(self, "max_wind_kmh", wind)
        _set(self, "activities", _choices("activities", self.activities, ACTIVITIES))
        _set(
            self,
            "destination_sizes",
            _choices("destination_sizes", self.destination_sizes, DESTINATION_SIZES),
        )

    @property
    def horizon(self) -> timedelta:
        """Length of the rolling search window (24 hours per selected day)."""
        return timedelta(hours=24 * self.days)


@dataclass(frozen=True, kw_only=True)
class WeatherRecord:
    """One normalized weather row: a current observation or a forecast period.

    Field names and order match RECORD_FIELDS. ``retrieved_at_utc`` is when the
    response arrived; ``valid_at_utc`` is the provider's observation/forecast
    time. Both are kept separately as aware UTC datetimes.
    """

    schema_version: int = SCHEMA_VERSION
    fetch_id: str
    city_id: str
    kind: str
    retrieved_at_utc: datetime
    valid_at_utc: datetime
    latitude: float
    longitude: float
    temperature_c: float | None = None
    wind_kmh: float | None = None
    precipitation_probability_pct: float | None = None
    humidity_pct: float | None = None
    cloud_pct: float | None = None
    provider_city_id: int
    provider_city_name: str

    def __post_init__(self) -> None:
        # A genuine int only: 1.0 or True compare equal to 1 but would serialize
        # as "1.0"/"True", which from_csv_row() could never read back.
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != SCHEMA_VERSION
        ):
            raise ValueError(f"schema_version must be the integer {SCHEMA_VERSION}")
        try:
            fetch_id = str(uuid.UUID(_text("fetch_id", self.fetch_id)))
        except ValueError:
            raise ValueError("fetch_id must be a UUID string") from None
        _set(self, "fetch_id", fetch_id)
        _set(self, "city_id", _city_id(self.city_id))
        if self.kind not in WEATHER_KINDS:
            raise ValueError("kind must be 'current' or 'forecast'")
        for name in _TIME_FIELDS:
            _set(self, name, _utc(name, getattr(self, name)))
        _set(self, "latitude", _number("latitude", self.latitude))
        _set(self, "longitude", _number("longitude", self.longitude))
        _in_range("latitude", self.latitude, -90, 90)
        _in_range("longitude", self.longitude, -180, 180)
        for name in _OPTIONAL_METRICS:
            _set(self, name, _number(name, getattr(self, name), optional=True))
        if self.wind_kmh is not None and self.wind_kmh < 0:
            raise ValueError("wind_kmh must not be negative")
        for name in ("precipitation_probability_pct", "humidity_pct", "cloud_pct"):
            _in_range(name, getattr(self, name), 0, 100)
        if self.kind == "current" and self.precipitation_probability_pct is not None:
            raise ValueError("current observations have no precipitation probability")
        if (
            isinstance(self.provider_city_id, bool)
            or not isinstance(self.provider_city_id, int)
            or self.provider_city_id <= 0
        ):
            raise ValueError("provider_city_id must be a positive integer")
        _set(self, "provider_city_name", _text("provider_city_name", self.provider_city_name))

    @staticmethod
    def new_fetch_id() -> str:
        """Identifier shared by every record from one fresh HTTP response."""
        return str(uuid.uuid4())

    @property
    def key(self) -> tuple[str, str, str, datetime]:
        """Identity used to make repeated saves of the same record idempotent."""
        return (self.fetch_id, self.city_id, self.kind, self.valid_at_utc)

    @property
    def lead_time(self) -> timedelta:
        """How far ahead of retrieval this record is valid (negative for observations)."""
        return self.valid_at_utc - self.retrieved_at_utc

    def to_csv_row(self) -> dict[str, str]:
        """Serialize for CSV: ISO UTC times and blank cells for missing values."""
        row: dict[str, str] = {}
        for name in RECORD_FIELDS:
            value = getattr(self, name)
            if value is None:
                row[name] = ""
            elif isinstance(value, datetime):
                row[name] = format_utc(value)
            elif isinstance(value, float):
                row[name] = repr(value)  # shortest exact round-trip form
            else:
                row[name] = str(value)
        return row

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> WeatherRecord:
        """Rebuild a validated record from one CSV row."""
        if set(row) != set(RECORD_FIELDS):
            raise ValueError("row does not match the weather record columns")
        values: dict[str, object] = {}
        try:
            values["schema_version"] = int(row["schema_version"])
            values["provider_city_id"] = int(row["provider_city_id"])
        except (TypeError, ValueError):
            raise ValueError("schema_version and provider_city_id must be integers") from None
        for name in ("fetch_id", "city_id", "kind", "provider_city_name"):
            values[name] = row[name]
        for name in _TIME_FIELDS:
            values[name] = parse_utc(name, row[name])
        for name in _FLOAT_FIELDS:
            text = (row[name] or "").strip()
            if not text:
                values[name] = None
                continue
            try:
                values[name] = float(text)
            except ValueError:
                raise ValueError(f"{name} is not a number") from None
        return cls(**values)

    def __lt__(self, other: object) -> bool:
        """Chronological order, so ``sorted(records)`` follows valid time."""
        if not isinstance(other, WeatherRecord):
            return NotImplemented
        return (self.valid_at_utc, self.city_id, self.kind, self.retrieved_at_utc) < (
            other.valid_at_utc,
            other.city_id,
            other.kind,
            other.retrieved_at_utc,
        )

    def __str__(self) -> str:
        def show(value: float | None, unit: str) -> str:
            return "n/a" if value is None else f"{value:g} {unit}"

        return (
            f"{self.kind} {self.city_id} at {format_utc(self.valid_at_utc)}: "
            f"{show(self.temperature_c, '°C')}, wind {show(self.wind_kmh, 'km/h')}, "
            f"rain probability {show(self.precipitation_probability_pct, '%')}"
        )
