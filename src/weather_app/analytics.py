"""P3.3 analytical engine: trip suitability ranking, cross-city weather comparison
and forecast periods meeting all preferences.

Implements the rules in PHASE2_SCOPE.md ("Product rules" and "P2.4 shared data
and calculation specification"). The engine is pure: it performs no network
access, reads no credentials or files, writes nothing and never reads the
clock. Callers pass one explicit, common UTC search time.

All three analyses are columns of the same result dictionaries, so the Searcher
and the Dashboard consume one calculation:

* ranking: ``weather_match_pct``, ``travel_penalty`` and ``final_score`` in the
  agreed order;
* weather comparison: ``mean_temperature_c``, ``max_precipitation_probability_pct``
  (the highest single-period probability, not a whole-trip probability) and
  ``max_wind_kmh`` over the same daytime periods;
* simultaneous suitability: ``suitable_period_count`` and ``all_preferences_pct``.

Values are unrounded; rounding belongs to display.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from weather_app.models import (
    Destination,
    SearchPreferences,
    WeatherRecord,
    format_utc,
)

LOCAL_TIMEZONE = ZoneInfo("Europe/Madrid")
DAYTIME_START_HOUR = 9  # inclusive, Europe/Madrid local time
DAYTIME_END_HOUR = 18  # exclusive
PERIOD_STEP = timedelta(hours=3)  # native provider forecast grid
FORECAST_MAX_AGE = timedelta(hours=3)  # older than this is stale; equal is allowed
MAX_TRAVEL_PENALTY = 5.0

AVAILABLE = "available"
UNAVAILABLE = "unavailable"

# Unavailable reasons, in the precedence order of the specification.
FETCH_FAILED = "fetch_failed"
INVALID_DATA = "invalid_data"
STALE_FORECAST = "stale_forecast"
DUPLICATE_PERIODS = "duplicate_periods"
MISSING_PERIODS = "missing_periods"
MISSING_METRICS = "missing_metrics"
UNAVAILABLE_REASONS = (
    FETCH_FAILED,
    INVALID_DATA,
    STALE_FORECAST,
    DUPLICATE_PERIODS,
    MISSING_PERIODS,
    MISSING_METRICS,
)

RESULT_FIELDS = (
    "city_id",
    "status",
    "reason",
    "run_at_utc",
    "days",
    "forecast_retrieved_at_utc",
    "expected_periods",
    "evaluated_periods",
    "temperature_passes",
    "precipitation_passes",
    "wind_passes",
    "weather_match_pct",
    "travel_penalty",
    "final_score",
    "suitable_period_count",
    "all_preferences_pct",
    "mean_temperature_c",
    "max_precipitation_probability_pct",
    "max_wind_kmh",
)
_SCORED_FIELDS = RESULT_FIELDS[8:]  # pass counts, scores and statistics

_REQUIRED_METRICS = ("temperature_c", "precipitation_probability_pct", "wind_kmh")


def _check_run_at(run_at_utc: object) -> datetime:
    if not isinstance(run_at_utc, datetime):
        raise ValueError("invalid_input: run_at_utc must be a datetime")
    if run_at_utc.tzinfo is None or run_at_utc.utcoffset() is None:
        raise ValueError("invalid_input: run_at_utc must be timezone-aware UTC")
    if run_at_utc.utcoffset() != timedelta(0):
        raise ValueError("invalid_input: run_at_utc must be expressed in UTC")
    return run_at_utc.astimezone(timezone.utc)


def expected_period_times(run_at_utc: datetime, days: int) -> list[datetime]:
    """Native three-hour UTC times in the rolling window that fall in local daytime.

    The window is ``run_at < valid_at <= run_at + 24 * days hours``; daytime is
    Europe/Madrid 09:00 inclusive to 18:00 exclusive, so clock changes are
    handled by the local conversion rather than by a fixed UTC offset.
    """
    run_at = _check_run_at(run_at_utc)
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 5:
        raise ValueError("invalid_input: days must be a whole number from 1 to 5")
    end = run_at + timedelta(hours=24 * days)
    step_seconds = int(PERIOD_STEP.total_seconds())
    epoch_seconds = int(run_at.timestamp())
    first = (epoch_seconds // step_seconds + 1) * step_seconds  # strictly after run_at
    times = []
    current = datetime.fromtimestamp(first, tz=timezone.utc)
    while current <= end:
        if is_daytime(current):
            times.append(current)
        current += PERIOD_STEP
    return times


def is_daytime(moment_utc: datetime) -> bool:
    """True from 09:00 inclusive to 18:00 exclusive, Europe/Madrid local time."""
    local = moment_utc.astimezone(LOCAL_TIMEZONE)
    return DAYTIME_START_HOUR <= local.hour < DAYTIME_END_HOUR


def is_eligible(destination: Destination, preferences: SearchPreferences) -> bool:
    """ANY selected activity AND ANY selected size; an empty selection means All."""
    activity_ok = not preferences.activities or any(
        tag in preferences.activities for tag in destination.activities
    )
    size_ok = (
        not preferences.destination_sizes
        or destination.destination_size in preferences.destination_sizes
    )
    return activity_ok and size_ok


def ranking_key(row: Mapping, car_duration_min: float) -> tuple:
    """Sort key for available rows: unrounded final score and weather match
    descending, then driving minutes ascending, then city_id ascending."""
    return (-row["final_score"], -row["weather_match_pct"], car_duration_min, row["city_id"])


def _unavailable(base: dict, reason: str, retrieved_at: datetime | None) -> dict:
    row = dict(base)
    row["status"] = UNAVAILABLE
    row["reason"] = reason
    row["forecast_retrieved_at_utc"] = None if retrieved_at is None else format_utc(retrieved_at)
    row["evaluated_periods"] = 0
    for name in _SCORED_FIELDS:
        row[name] = None
    return row


def _analyse_one(
    destination: Destination,
    records: Sequence[WeatherRecord] | None,
    preferences: SearchPreferences,
    run_at: datetime,
    expected: list[datetime],
) -> dict:
    base = {name: None for name in RESULT_FIELDS}
    base.update(
        city_id=destination.city_id,
        run_at_utc=format_utc(run_at),
        days=preferences.days,
        expected_periods=len(expected),
    )

    if not records:
        return _unavailable(base, FETCH_FAILED, None)

    # Identity: one forecast group for this city, from one response.
    if not all(isinstance(r, WeatherRecord) for r in records):
        return _unavailable(base, INVALID_DATA, None)
    groups = {(r.fetch_id, r.retrieved_at_utc) for r in records}
    if len(groups) != 1 or any(
        r.city_id != destination.city_id or r.kind != "forecast" for r in records
    ):
        return _unavailable(base, INVALID_DATA, None)
    retrieved_at = records[0].retrieved_at_utc

    if max(timedelta(0), run_at - retrieved_at) > FORECAST_MAX_AGE:
        return _unavailable(base, STALE_FORECAST, retrieved_at)

    by_time: dict[datetime, WeatherRecord] = {}
    for record in records:
        if record.valid_at_utc in by_time:
            return _unavailable(base, DUPLICATE_PERIODS, retrieved_at)
        by_time[record.valid_at_utc] = record

    if not expected or any(time not in by_time for time in expected):
        return _unavailable(base, MISSING_PERIODS, retrieved_at)

    periods = [by_time[time] for time in expected]
    if any(getattr(p, name) is None for p in periods for name in _REQUIRED_METRICS):
        return _unavailable(base, MISSING_METRICS, retrieved_at)

    temperature_ok = [
        preferences.temperature_min_c <= p.temperature_c <= preferences.temperature_max_c
        for p in periods
    ]
    rain_ok = [
        p.precipitation_probability_pct <= preferences.max_precipitation_probability_pct
        for p in periods
    ]
    wind_ok = [p.wind_kmh <= preferences.max_wind_kmh for p in periods]

    evaluated = len(periods)
    passed = sum(temperature_ok) + sum(rain_ok) + sum(wind_ok)
    suitable = sum(t and r and w for t, r, w in zip(temperature_ok, rain_ok, wind_ok))
    weather_match = 100 * passed / (3 * evaluated)
    travel_penalty = min(destination.car_duration_min / 60, MAX_TRAVEL_PENALTY)

    row = dict(base)
    row.update(
        status=AVAILABLE,
        reason=None,
        forecast_retrieved_at_utc=format_utc(retrieved_at),
        evaluated_periods=evaluated,
        temperature_passes=sum(temperature_ok),
        precipitation_passes=sum(rain_ok),
        wind_passes=sum(wind_ok),
        weather_match_pct=weather_match,
        travel_penalty=travel_penalty,
        final_score=max(weather_match - travel_penalty, 0.0),
        suitable_period_count=suitable,
        all_preferences_pct=100 * suitable / evaluated,
        mean_temperature_c=sum(p.temperature_c for p in periods) / evaluated,
        max_precipitation_probability_pct=max(p.precipitation_probability_pct for p in periods),
        max_wind_kmh=max(p.wind_kmh for p in periods),
    )
    return row


def forecasts_from_service(results: Mapping[str, Mapping]) -> dict[str, list[WeatherRecord]]:
    """Turn ``WeatherService.forecast_many`` results into ``forecasts_by_city``.

    A city whose result carries an error contributes no records, so the
    engine reports it as ``fetch_failed``; the service's own error message
    stays with the caller for display. Only saved or cached records reach
    analysis, because the service returns no records after a failed save.
    """
    if not isinstance(results, Mapping):
        raise ValueError("invalid_input: service results must be a mapping by city_id")
    forecasts: dict[str, list[WeatherRecord]] = {}
    for city_id, result in results.items():
        if not isinstance(result, Mapping) or "records" not in result or "error" not in result:
            raise ValueError("invalid_input: each service result needs records and error")
        forecasts[city_id] = [] if result["error"] is not None else list(result["records"])
    return forecasts


def analyse_destinations(
    destinations: Sequence[Destination],
    forecasts_by_city: Mapping[str, Sequence[WeatherRecord]],
    preferences: SearchPreferences,
    run_at_utc: datetime,
) -> list[dict]:
    """Return the full ordered analysis for every eligible destination.

    Available rows come first, sorted by final score (descending), weather
    match (descending), driving minutes (ascending) and city_id. Unavailable
    rows follow, sorted by city_id. Destinations removed by the activity/size
    filters are omitted. Invalid inputs raise ``ValueError`` prefixed with
    ``invalid_input`` before any processing.
    """
    if not isinstance(preferences, SearchPreferences):
        raise ValueError("invalid_input: preferences must be SearchPreferences")
    run_at = _check_run_at(run_at_utc)
    if not isinstance(forecasts_by_city, Mapping):
        raise ValueError("invalid_input: forecasts_by_city must be a mapping")
    if isinstance(destinations, (str, bytes)) or not isinstance(destinations, Sequence):
        raise ValueError("invalid_input: destinations must be a sequence")
    seen: set[str] = set()
    for destination in destinations:
        if not isinstance(destination, Destination):
            raise ValueError("invalid_input: destinations must contain Destination objects")
        if destination.city_id in seen:
            raise ValueError(f"invalid_input: duplicate destination {destination.city_id}")
        seen.add(destination.city_id)

    expected = expected_period_times(run_at, preferences.days)
    drive_minutes = {d.city_id: d.car_duration_min for d in destinations}

    available: list[dict] = []
    unavailable: list[dict] = []
    for destination in destinations:
        if not is_eligible(destination, preferences):
            continue
        row = _analyse_one(
            destination,
            forecasts_by_city.get(destination.city_id),
            preferences,
            run_at,
            expected,
        )
        (available if row["status"] == AVAILABLE else unavailable).append(row)

    available.sort(key=lambda row: ranking_key(row, drive_minutes[row["city_id"]]))
    unavailable.sort(key=lambda row: row["city_id"])
    return available + unavailable
