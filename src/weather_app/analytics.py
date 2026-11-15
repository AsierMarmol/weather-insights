"""Pure validated forecast analytics for both application views.

SCORING.md owns the current formula; scoring.py supplies slot functions and
80/20 aggregation. This module applies coverage, freshness and driving rules
once, returning canonical final_score values for whole windows and daily
slices. It performs no HTTP, credential access, file writes or clock reads.

Source means/maxima support comparisons and executive summaries. Exact target
pass counts are retained as internal diagnostics, not extra displayed scores.
All values remain unrounded until presentation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import cast

from weather_app.scoring import aggregate, slot_score

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
# older than this is stale; equal is allowed
FORECAST_MAX_AGE = timedelta(hours=3)
MAX_TRAVEL_PENALTY = 15.0
TRAVEL_POINTS_PER_HOUR = 2.0

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
    "mean_precipitation_probability_pct",
    "mean_wind_kmh",
    "max_precipitation_probability_pct",
    "max_wind_kmh",
)
_SCORED_FIELDS = RESULT_FIELDS[8:]  # pass counts, scores and statistics

_REQUIRED_METRICS = (
    "temperature_c",
    "precipitation_probability_pct",
    "wind_kmh",
)


def _check_run_at(run_at_utc: object) -> datetime:
    if not isinstance(run_at_utc, datetime):
        raise ValueError("invalid_input: run_at_utc must be a datetime")
    if run_at_utc.tzinfo is None or run_at_utc.utcoffset() is None:
        raise ValueError(
            "invalid_input: run_at_utc must be timezone-aware UTC"
        )
    if run_at_utc.utcoffset() != timedelta(0):
        raise ValueError("invalid_input: run_at_utc must be expressed in UTC")
    return run_at_utc.astimezone(timezone.utc)


def expected_period_times(run_at_utc: datetime, days: int) -> list[datetime]:
    """Native three-hour UTC times in the rolling window that fall in local
    daytime.

    The window is ``run_at < valid_at <= run_at + 24 * days hours``; daytime
    is
    Europe/Madrid 09:00 inclusive to 18:00 exclusive, so clock changes are
    handled by the local conversion rather than by a fixed UTC offset.
    """
    run_at = _check_run_at(run_at_utc)
    if (
        isinstance(days, bool)
        or not isinstance(days, int)
        or not 1 <= days <= 5
    ):
        raise ValueError(
            "invalid_input: days must be a whole number from 1 to 5"
        )
    end = run_at + timedelta(hours=24 * days)
    step_seconds = int(PERIOD_STEP.total_seconds())
    epoch_seconds = int(run_at.timestamp())
    first = (
        epoch_seconds // step_seconds + 1
    ) * step_seconds  # strictly after run_at
    times = []
    current = datetime.fromtimestamp(first, tz=timezone.utc)
    while current <= end:
        if is_daytime(current):
            times.append(current)
        current += PERIOD_STEP
    return times


def is_daytime(moment_utc: datetime) -> bool:
    """True from 09:00 inclusive to 18:00 exclusive, Europe/Madrid local time.
    """
    local = moment_utc.astimezone(LOCAL_TIMEZONE)
    return DAYTIME_START_HOUR <= local.hour < DAYTIME_END_HOUR


def is_eligible(
    destination: Destination, preferences: SearchPreferences
) -> bool:
    """ANY selected activity AND ANY selected size; an empty selection means
    All.
    """
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
    return (
        -row["final_score"],
        -row["weather_match_pct"],
        car_duration_min,
        row["city_id"],
    )


def _unavailable(
    base: dict, reason: str, retrieved_at: datetime | None
) -> dict:
    row = dict(base)
    row["status"] = UNAVAILABLE
    row["reason"] = reason
    row["forecast_retrieved_at_utc"] = (
        None if retrieved_at is None else format_utc(retrieved_at)
    )
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
    base: dict[str, str | float | None] = {
        name: None for name in RESULT_FIELDS
    }
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
        r.city_id != destination.city_id or r.kind != "forecast"
        for r in records
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
    required = _REQUIRED_METRICS + (
        ("cloud_pct",) if preferences.scoring_mode == "dashboard" else ()
    )
    if any(getattr(p, name) is None for p in periods for name in required):
        return _unavailable(base, MISSING_METRICS, retrieved_at)

    scored = [slot_score(p, preferences) for p in periods]
    temperature_ok, rain_ok, wind_ok = zip(*(flags for _, flags in scored))
    evaluated = len(periods)
    suitable = sum(all(flags) for _, flags in scored)
    weather_match = aggregate([score for score, _ in scored])
    travel_penalty = min(destination.car_duration_min / 60
                         * TRAVEL_POINTS_PER_HOUR, MAX_TRAVEL_PENALTY)

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
        mean_temperature_c=sum(
            cast(float, p.temperature_c) for p in periods) / evaluated,
        mean_precipitation_probability_pct=sum(
            cast(float, p.precipitation_probability_pct) for p in periods
        ) / evaluated,
        mean_wind_kmh=sum(
            cast(float, p.wind_kmh) for p in periods) / evaluated,
        max_precipitation_probability_pct=max(
            cast(float, p.precipitation_probability_pct) for p in periods
        ),
        max_wind_kmh=max(cast(float, p.wind_kmh) for p in periods),
    )
    return row


def forecasts_from_service(
    results: Mapping[str, Mapping],
) -> dict[str, list[WeatherRecord]]:
    """Turn ``WeatherService.forecast_many`` results into
    ``forecasts_by_city``.

    A city whose result carries an error contributes no records, so the
    engine reports it as ``fetch_failed``; the service's own error message
    stays with the caller for display. Only saved or cached records reach
    analysis, because the service returns no records after a failed save.
    """
    if not isinstance(results, Mapping):
        raise ValueError(
            "invalid_input: service results must be a mapping by city_id"
        )
    forecasts: dict[str, list[WeatherRecord]] = {}
    for city_id, result in results.items():
        if (
            not isinstance(result, Mapping)
            or "records" not in result
            or "error" not in result
        ):
            raise ValueError(
                "invalid_input: each service result needs records and error"
            )
        forecasts[city_id] = (
            [] if result["error"] is not None else list(result["records"])
        )
    return forecasts


def _validate_inputs(destinations, forecasts_by_city, preferences, run_at_utc):
    if not isinstance(preferences, SearchPreferences):
        raise ValueError(
            "invalid_input: preferences must be SearchPreferences"
        )
    run_at = _check_run_at(run_at_utc)
    if not isinstance(forecasts_by_city, Mapping):
        raise ValueError("invalid_input: forecasts_by_city must be a mapping")
    if isinstance(destinations, (str, bytes)) or not isinstance(
        destinations, Sequence
    ):
        raise ValueError("invalid_input: destinations must be a sequence")
    seen: set[str] = set()
    for destination in destinations:
        if not isinstance(destination, Destination):
            raise ValueError(
                "invalid_input: destinations must contain Destination objects"
            )
        if destination.city_id in seen:
            raise ValueError(
                f"invalid_input: duplicate destination {destination.city_id}"
            )
        seen.add(destination.city_id)
    return run_at


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
    run_at = _validate_inputs(
        destinations, forecasts_by_city, preferences, run_at_utc
    )

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

    available.sort(
        key=lambda row: ranking_key(row, drive_minutes[row["city_id"]])
    )
    unavailable.sort(key=lambda row: row["city_id"])
    return available + unavailable


def daily_weather(destinations, forecasts, preferences, run_at_utc):
    """Score each successive 24-hour slice of the same saved snapshot.

    Reuse the full engine's validation, daytime grid and weighted scoring.
    Freshness is evaluated at the overview load time, never at a future
    day's start. Missing days remain unavailable; no interpolation occurs.
    """
    run_at_utc = _validate_inputs(
        destinations, forecasts, preferences, run_at_utc
    )
    times = expected_period_times(run_at_utc, preferences.days)
    cells = []
    for day in range(1, preferences.days + 1):
        start = run_at_utc + timedelta(days=day - 1)
        end = run_at_utc + timedelta(days=day)
        expected = [t for t in times if start < t <= end]
        for destination in destinations:
            if not is_eligible(destination, preferences):
                continue
            row = _analyse_one(
                destination, forecasts.get(destination.city_id),
                preferences, run_at_utc, expected,
            )
            cells.append({
                "city_id": destination.city_id, "day": day,
                "start": format_utc(start), "end": format_utc(end),
                "status": row["status"], "reason": row["reason"],
                "score": row["final_score"],
                "expected_periods": row["expected_periods"],
                "evaluated_periods": row["evaluated_periods"],
            })
    return cells


def destination_ranks(rows):
    """Shared Dashboard ranks from unrounded final scores (ties: 1, 1, 3)."""
    scores = {r["city_id"]: r["final_score"] for r in rows
              if r["status"] == AVAILABLE}
    rank_by_score = {}
    for rank, score in enumerate(sorted(scores.values(), reverse=True), 1):
        rank_by_score.setdefault(score, rank)
    return {city: rank_by_score[score] for city, score in scores.items()}
