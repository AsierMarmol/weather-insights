"""P4.4 Dashboard: an independent weather overview of mainland Spain.

The Dashboard works without a Searcher run. It always shows all catalog
destinations on a map and, after an explicit Load/refresh, ranks them by
weather alone for its own next 1-5 days using the seasonal default
criteria (product_defaults.json). It reuses the shared request/save path
(``searcher.search_destinations`` -> ``WeatherService`` -> analytics), so
suitable saved forecasts are reused, missing or stale ones are fetched with
the established pacing and every fresh response is saved automatically.

Weather score = the engine's ``weather_match_pct`` (no driving penalty).
Weather rank: highest unrounded score first; equal scores share a rank
(competition ranking: 1, 1, 3) and ``city_id`` orders destinations within a
tie. This is deliberately different from the Searcher's trip ranking.

Dashboard controls, results and errors use ``dashboard_*`` session keys and
never read or change the Searcher's ``search_*`` state. Hovering, filtering
and navigation never make requests; only the Load/refresh button does.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from weather_app import searcher
from weather_app.analytics import (
    AVAILABLE,
    FORECAST_MAX_AGE,
    RESULT_FIELDS,
    UNAVAILABLE,
)
from weather_app.client import APIError
from weather_app.config import load_product_defaults
from weather_app.models import ACTIVITIES, DESTINATION_SIZES
from weather_app.storage import CatalogError, load_destinations

MADRID = ZoneInfo("Europe/Madrid")
ALL = "All"
DAY_OPTIONS = (1, 2, 3, 4, 5)
NO_DATA_COLOUR = "#9e9e9e"
# Mercator zoom that keeps every mainland catalog destination in view with
# a small margin (checked visually at desktop and phone widths).
MAP_SCALE = 22
MAP_CONFIG = {"scrollZoom": False}

DAYS_KEY = "dashboard_days"
LOAD_KEY = "dashboard_load"
OVERVIEW_KEY = "dashboard_overview"
ERROR_KEY = "dashboard_error"
METRIC_KEY = "dashboard_metric"
FILTER_KEYS = {
    "destinations": "dashboard_destinations",
    "activities": "dashboard_activities",
    "sizes": "dashboard_sizes",
}

# Scores and statistics an available row must carry as finite numbers.
_AVAILABLE_NUMBERS = RESULT_FIELDS[6:]

SLOT_NOTE = (
    "Slots are three-hour daytime forecast slots (09:00-18:00 Madrid "
    "time). Coverage 9/9 means all nine required slots have data; it is "
    "not nine days or nine hours of good weather."
)

# Weather comparison metrics: (chart title, axis label, aggregation note).
COMPARISON_METRICS = {
    "mean_temperature_c": (
        "Average daytime temperature",
        "Average daytime temperature (°C)",
        "Average temperature over every three-hour daytime forecast slot "
        "in the window.",
    ),
    "max_precipitation_probability_pct": (
        "Highest precipitation probability",
        "Highest slot precipitation probability (%)",
        "Highest probability in any single three-hour daytime slot. "
        "It is not the probability of rain over the whole window.",
    ),
    "max_wind_kmh": (
        "Strongest daytime wind",
        "Highest slot wind speed (km/h)",
        "Highest sustained wind speed (not gusts) in any single three-hour "
        "daytime slot.",
    ),
}


class DashboardDataError(ValueError):
    """Analysis or catalog rows do not match the shared P2.4 shape."""


# ---------------------------------------------------------------------------
# Criteria and ranking (pure)
# ---------------------------------------------------------------------------


def overview_preferences(now_utc: datetime, defaults: Mapping, days: int):
    """Seasonal default criteria for a Dashboard window of ``days`` days.

    Temperature comes from the Europe/Madrid season of ``now_utc``;
    precipitation and wind limits and All filters come from the defaults.
    """
    if days not in DAY_OPTIONS:
        raise ValueError("The Dashboard window must be 1-5 days.")
    return replace(searcher.initial_preferences(now_utc, defaults), days=days)


def weather_ranks(analysis_rows: Iterable[Mapping]) -> dict[str, int]:
    """Weather-only competition ranks for available rows, by city_id.

    The highest unrounded ``weather_match_pct`` ranks first; equal scores
    share a rank and the next distinct score skips the tied places.
    Driving time is never used.
    """
    scores = {
        row["city_id"]: row["weather_match_pct"]
        for row in analysis_rows
        if row["status"] == AVAILABLE
    }
    ordered = sorted(scores.values(), reverse=True)
    return {city: ordered.index(score) + 1 for city, score in scores.items()}


# ---------------------------------------------------------------------------
# Result table (pure)
# ---------------------------------------------------------------------------


def _parse_utc(name: str, value: object) -> datetime:
    if not isinstance(value, str):
        raise DashboardDataError(f"{name} must be an ISO UTC string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise DashboardDataError(
            f"{name} is not a valid ISO timestamp"
        ) from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DashboardDataError(f"{name} must be a UTC timestamp")
    return parsed.astimezone(timezone.utc)


def _is_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _activities(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(p.strip() for p in value.split(";") if p.strip())
    if isinstance(value, Iterable):
        return tuple(str(part) for part in value)
    raise DashboardDataError("catalog activities must be a list")


def _check_row(position: int, row: Mapping) -> None:
    missing = [name for name in RESULT_FIELDS if name not in row]
    if missing:
        raise DashboardDataError(
            f"result row {position} lacks {', '.join(missing)}"
        )
    city_id = row["city_id"]
    if row["status"] == AVAILABLE:
        bad = [n for n in _AVAILABLE_NUMBERS if not _is_number(row[n])]
        if bad:
            raise DashboardDataError(
                f"available row {city_id} has invalid {', '.join(bad)}"
            )
    elif row["status"] == UNAVAILABLE:
        if not row["reason"]:
            raise DashboardDataError(
                f"unavailable row {city_id} has no reason"
            )
    else:
        raise DashboardDataError(
            f"unknown status {row['status']!r} for {city_id}"
        )


def prepare_frame(
    analysis_rows: Sequence[Mapping], catalog_rows: Sequence[Mapping]
) -> pd.DataFrame:
    """Join engine rows to the catalog and order them by weather rank.

    ``rank`` is the weather-only rank (see ``weather_ranks``). Ranked rows
    come first (rank, then city_id); unavailable rows follow by city_id
    with no rank. Raises ``DashboardDataError`` for rows outside the
    shared result contract.
    """
    catalog = {}
    for place in catalog_rows:
        if not place.get("city_id"):
            raise DashboardDataError("catalog row without city_id")
        catalog[place["city_id"]] = place

    records, searches, seen = [], set(), set()
    for position, row in enumerate(analysis_rows):
        _check_row(position, row)
        city_id = row["city_id"]
        if city_id not in catalog:
            raise DashboardDataError(
                f"result city {city_id!r} is not in the catalog"
            )
        if city_id in seen:
            raise DashboardDataError(f"result city {city_id!r} repeats")
        seen.add(city_id)
        run_at = _parse_utc("run_at_utc", row["run_at_utc"])
        searches.add((run_at, row["days"]))
        retrieved = row["forecast_retrieved_at_utc"]
        place = catalog[city_id]
        record = {name: row[name] for name in RESULT_FIELDS}
        record.update(
            destination=place["city"],
            region=place.get("region", ""),
            activities=_activities(place.get("activities", ())),
            destination_size=place.get("destination_size", ""),
            run_at_utc=run_at,
            forecast_retrieved_at_utc=(
                None
                if retrieved is None
                else _parse_utc("forecast_retrieved_at_utc", retrieved)
            ),
        )
        records.append(record)
    if len(searches) > 1:
        raise DashboardDataError("results come from more than one search")

    ranks = weather_ranks(analysis_rows)
    for record in records:
        record["rank"] = ranks.get(record["city_id"])
    records.sort(
        key=lambda r: (r["rank"] is None, r["rank"] or 0, r["city_id"])
    )
    columns = [
        "rank", "destination", "region", "activities", "destination_size",
        *RESULT_FIELDS,
    ]
    frame = pd.DataFrame.from_records(records, columns=columns)
    frame["rank"] = frame["rank"].astype("Int64")  # <NA> when unavailable
    return frame


def _clean(selection: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(item for item in (selection or ()) if item != ALL)


def matches(
    city_id: str,
    activities: Iterable[str],
    size: str,
    chosen_ids: Iterable[str] | None = None,
    chosen_activities: Iterable[str] | None = None,
    chosen_sizes: Iterable[str] | None = None,
) -> bool:
    """ANY chosen value within a group; AND between groups; All = no limit."""
    ids, tags, kinds = (
        _clean(chosen_ids),
        _clean(chosen_activities),
        _clean(chosen_sizes),
    )
    return (
        (not ids or city_id in ids)
        and (not tags or bool(set(tags).intersection(activities)))
        and (not kinds or size in kinds)
    )


def filter_frame(
    frame: pd.DataFrame,
    destinations: Iterable[str] | None = None,
    activities: Iterable[str] | None = None,
    sizes: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Rows matching the optional filters; order and ranks are unchanged."""
    if frame.empty:
        return frame
    mask = [
        matches(row.city_id, row.activities, row.destination_size,
                destinations, activities, sizes)
        for row in frame.itertuples()
    ]
    return frame[mask]


def search_context(frame: pd.DataFrame) -> dict | None:
    """Common load time, forecast window and retrieval times."""
    if frame.empty:
        return None
    run_at = frame["run_at_utc"].iloc[0]
    days = int(frame["days"].iloc[0])
    retrieved = [
        value
        for value in frame["forecast_retrieved_at_utc"]
        if value is not None and not pd.isna(value)
    ]
    oldest = min(retrieved) if retrieved else None
    return {
        "run_at_utc": run_at,
        "days": days,
        "window_end_utc": run_at + timedelta(hours=24 * days),
        "oldest_retrieved_at_utc": oldest,
        "newest_retrieved_at_utc": max(retrieved) if retrieved else None,
        "oldest_age": (
            None if oldest is None else max(timedelta(0), run_at - oldest)
        ),
    }


def _reason(city_id: str, code: str | None, errors: Mapping) -> str:
    code = errors.get(city_id, code)
    return searcher.MESSAGES.get(code, "Forecast unavailable.")


# ---------------------------------------------------------------------------
# Map (pure)
# ---------------------------------------------------------------------------


def map_points(
    catalog_rows: Sequence[Mapping],
    frame: pd.DataFrame | None = None,
    errors: Mapping | None = None,
) -> list[dict]:
    """One point per catalog destination, with its hover text.

    Destinations without a loaded result are ``not_loaded``; engine rows
    marked unavailable are ``unavailable``. Neither gets a temperature,
    score or rank.
    """
    errors = errors or {}
    results = {} if frame is None else {
        row["city_id"]: row for row in frame.to_dict("records")
    }
    ranked_total = sum(
        1 for row in results.values() if row["status"] == AVAILABLE
    )
    points = []
    for place in catalog_rows:
        tags = _activities(place.get("activities", ()))
        point = {
            "city_id": place["city_id"],
            "city": place["city"],
            "latitude": float(place["latitude"]),
            "longitude": float(place["longitude"]),
            "activities": tags,
            "destination_size": place.get("destination_size", ""),
            "status": "not_loaded",
            "rank": None,
            "weather_score": None,
            "mean_temperature_c": None,
        }
        heading = (
            f"<b>{point['city']}</b><br>Activities: {', '.join(tags)}"
        )
        row = results.get(place["city_id"])
        if row is None:
            point["hover"] = (
                f"{heading}<br>Weather not loaded. Choose the days and "
                "click Load weather overview."
            )
        elif row["status"] == AVAILABLE:
            point.update(
                status="ranked",
                rank=int(row["rank"]),
                weather_score=row["weather_match_pct"],
                mean_temperature_c=row["mean_temperature_c"],
            )
            point["hover"] = (
                f"{heading}<br>Average daytime temperature: "
                f"{row['mean_temperature_c']:.1f} °C"
                f"<br>Weather rank: {point['rank']} of {ranked_total}"
                f"<br>Weather score: {row['weather_match_pct']:.1f}%"
            )
        else:
            point["status"] = "unavailable"
            point["hover"] = (
                f"{heading}<br>No weather rank: "
                f"{_reason(place['city_id'], row['reason'], errors)}"
            )
        points.append(point)
    return points


def map_figure(
    points: Sequence[Mapping], highlighted: Iterable[str] | None = None
) -> go.Figure:
    """Mainland-Spain map with every destination as a marker.

    Ranked destinations are coloured by weather score; destinations
    without a result are neutral grey. ``highlighted`` city_ids stay
    opaque and the rest are dimmed, never removed.
    """
    keep = None if highlighted is None else set(highlighted)

    def opacity(group):
        return [
            0.95 if keep is None or p["city_id"] in keep else 0.2
            for p in group
        ]

    ranked = sorted(
        (p for p in points if p["status"] == "ranked"),
        key=lambda p: (p["rank"], p["city_id"]),
    )
    others = sorted(
        (p for p in points if p["status"] != "ranked"),
        key=lambda p: p["city_id"],
    )
    loaded = any(p["status"] != "not_loaded" for p in points)
    figure = go.Figure()
    figure.add_trace(
        go.Scattergeo(
            name="Weather score",
            lat=[p["latitude"] for p in ranked],
            lon=[p["longitude"] for p in ranked],
            customdata=[p["city_id"] for p in ranked],
            hovertext=[p["hover"] for p in ranked],
            hovertemplate="%{hovertext}<extra></extra>",
            mode="markers",
            marker={
                "size": 12,
                "color": [p["weather_score"] for p in ranked],
                "cmin": 0,
                "cmax": 100,
                "colorscale": "RdYlGn",
                "colorbar": {"title": {"text": "Weather score (%)"}},
                "opacity": opacity(ranked),
                "line": {"width": 0.6, "color": "#333333"},
            },
        )
    )
    figure.add_trace(
        go.Scattergeo(
            name="No weather rank" if loaded else "Weather not loaded",
            lat=[p["latitude"] for p in others],
            lon=[p["longitude"] for p in others],
            customdata=[p["city_id"] for p in others],
            hovertext=[p["hover"] for p in others],
            hovertemplate="%{hovertext}<extra></extra>",
            mode="markers",
            marker={
                "size": 10,
                "color": NO_DATA_COLOUR,
                "opacity": opacity(others),
                "line": {"width": 0.6, "color": "#333333"},
            },
        )
    )
    # Centre on the middle of the catalog coordinates and zoom to mainland
    # Spain. (Plotly's fitbounds="locations" centred this map about 3° too
    # far north and left the markers in a small part of the frame.)
    lats = [p["latitude"] for p in points] or [40.0]
    lons = [p["longitude"] for p in points] or [-3.7]
    figure.update_geos(
        center={
            "lat": (min(lats) + max(lats)) / 2,
            "lon": (min(lons) + max(lons)) / 2,
        },
        projection_scale=MAP_SCALE,
        projection_type="mercator",
        resolution=50,
        showcountries=True,
        countrycolor="#8c8c8c",
        showland=True,
        landcolor="#f2efe9",
        showocean=True,
        oceancolor="#dceaf5",
        showlakes=False,
    )
    figure.update_layout(
        height=560,
        margin={"l": 0, "r": 0, "t": 35, "b": 0},
        legend={"orientation": "h", "y": -0.02},
    )
    return figure


# ---------------------------------------------------------------------------
# Companion charts (pure)
# ---------------------------------------------------------------------------


def _available(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame["status"] == AVAILABLE]


def _labels(rows: pd.DataFrame) -> list[str]:
    return [f"{r}. {n}" for r, n in zip(rows["rank"], rows["destination"])]


def _bar_layout(figure: go.Figure, title: str, axis: str, rows: int) -> None:
    figure.update_layout(
        title=title,
        xaxis_title=axis,
        yaxis_title="Destination (weather rank)",
        yaxis_autorange="reversed",
        height=max(260, 90 + 20 * rows),
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )


def weather_score_chart(frame: pd.DataFrame) -> go.Figure:
    """Weather score per destination in weather-rank order (best on top)."""
    rows = _available(frame)
    figure = go.Figure(
        go.Bar(
            x=rows["weather_match_pct"].tolist(),
            y=_labels(rows),
            orientation="h",
            customdata=rows["mean_temperature_c"].tolist(),
            hovertemplate=(
                "%{y}<br>Weather score: %{x:.1f}%"
                "<br>Average daytime temperature: %{customdata:.1f} °C"
                "<extra></extra>"
            ),
        )
    )
    _bar_layout(
        figure,
        "Weather ranking: weather score by destination",
        "Weather score (% of temperature, rain and wind checks met; "
        "no driving penalty)",
        len(rows),
    )
    figure.update_xaxes(range=[0, 100])
    return figure


def _limits(preferences: object, metric: str) -> tuple:
    if preferences is None:
        return None, None
    if metric == "mean_temperature_c":
        return (
            getattr(preferences, "temperature_min_c", None),
            getattr(preferences, "temperature_max_c", None),
        )
    name = (
        "max_precipitation_probability_pct"
        if metric == "max_precipitation_probability_pct"
        else "max_wind_kmh"
    )
    return None, getattr(preferences, name, None)


def comparison_chart(
    frame: pd.DataFrame, metric: str, preferences: object = None
) -> go.Figure:
    """Compare one weather metric across destinations, marking limits."""
    if metric not in COMPARISON_METRICS:
        raise ValueError(f"unknown comparison metric {metric!r}")
    title, axis, _ = COMPARISON_METRICS[metric]
    rows = _available(frame)
    figure = go.Figure(
        go.Bar(
            x=rows[metric].tolist(),
            y=_labels(rows),
            orientation="h",
            hovertemplate=f"%{{y}}<br>{axis}: %{{x:.1f}}<extra></extra>",
        )
    )
    low, high = _limits(preferences, metric)
    # The limit is named in the title: an annotation inside the plot was
    # hidden behind the first bar.
    heading = f"{title} across destinations"
    if low is not None and high is not None:
        figure.add_vrect(
            x0=low, x1=high, fillcolor="green", opacity=0.12, line_width=0,
        )
        heading += f" (seasonal range {low:g}-{high:g} °C shaded)"
    elif high is not None:
        figure.add_vline(x=high, line_dash="dash")
        unit = "%" if metric == "max_precipitation_probability_pct" else (
            " km/h"
        )
        heading += f" (limit {high:g}{unit} dashed)"
    _bar_layout(figure, heading, axis, len(rows))
    return figure


def all_preferences_chart(frame: pd.DataFrame) -> go.Figure:
    """Share of daytime slots meeting all three criteria at once."""
    rows = _available(frame)
    counts = [
        f"{int(ok)}/{int(total)} slots"
        for ok, total in zip(
            rows["suitable_period_count"], rows["evaluated_periods"]
        )
    ]
    figure = go.Figure(
        go.Bar(
            x=rows["all_preferences_pct"].tolist(),
            y=_labels(rows),
            orientation="h",
            text=counts,
            textposition="auto",
            hovertemplate=(
                "%{y}<br>%{x:.1f}% of slots (%{text})<extra></extra>"
            ),
        )
    )
    _bar_layout(
        figure,
        "Three-hour daytime slots meeting all three criteria",
        "Slots meeting temperature, rain and wind criteria together (%)",
        len(rows),
    )
    figure.update_xaxes(range=[0, 100])
    return figure


# ---------------------------------------------------------------------------
# Streamlit rendering
# ---------------------------------------------------------------------------


def _madrid(value: datetime) -> str:
    return value.astimezone(MADRID).strftime("%a %d %b %Y, %H:%M %Z")


def _age(delta: timedelta) -> str:
    minutes = int(delta.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d} min"


def _criteria(preferences) -> str:
    return (
        f"{preferences.temperature_min_c:g}-"
        f"{preferences.temperature_max_c:g} °C · precipitation probability "
        f"≤ {preferences.max_precipitation_probability_pct:g}% · wind ≤ "
        f"{preferences.max_wind_kmh:g} km/h"
    )


def _remember(key: str) -> None:
    """Keep a widget's value while Streamlit hides it on the Searcher."""
    st.session_state[f"_saved_{key}"] = st.session_state[key]


def _keep_all_exclusive(key: str) -> None:
    st.session_state[key] = searcher.normalize_all_selection(
        st.session_state.get(key, [])
    )
    _remember(key)


def _seed(key: str, valid, default) -> None:
    """Restore a widget value from its saved copy before drawing it."""
    if key in st.session_state and valid(st.session_state[key]):
        return
    saved = st.session_state.get(f"_saved_{key}")
    st.session_state[key] = saved if valid(saved) else default


def _multiselect(label, key, options, help_text, format_func=str):
    _seed(
        key,
        lambda v: bool(v) and all(item in options for item in v),
        [ALL],
    )
    return st.multiselect(
        label, options, key=key, format_func=format_func,
        on_change=_keep_all_exclusive, args=(key,), help=help_text,
    )


def _ordered(values: Iterable[str], canonical: Sequence[str]) -> list[str]:
    present = set(values)
    extra = sorted(present - set(canonical))
    return [v for v in canonical if v in present] + extra


def _load(catalog, defaults, days: int) -> None:
    """Run the shared request/save/analysis path for every destination."""
    run_at = searcher.utc_now()
    preferences = overview_preferences(run_at, defaults, days)
    progress = st.progress(0.0, text="Loading the weather overview…")
    names = {d.city_id: d.city for d in catalog}

    def update(done, total, city_id, result):
        progress.progress(
            done / total, text=f"{done}/{total} · {names[city_id]}"
        )

    state = st.session_state
    try:
        service = searcher.get_service()
        result = searcher.search_destinations(
            catalog, preferences, service, run_at, update
        )
    except APIError as error:
        state[ERROR_KEY] = {
            "code": error.code,
            # Fixed setup guidance from config; never the key itself.
            "guidance": (
                error.message if error.code == "authentication" else None
            ),
        }
    except ValueError:
        state[ERROR_KEY] = {"code": "invalid_input", "guidance": None}
    else:
        state[OVERVIEW_KEY] = {
            "rows": result["rows"],
            "errors": result["errors"],
            "cached": result["cached"],
            "storage_failure": result.get("storage_failure"),
            "run_at": run_at,
            "preferences": preferences,
        }
        state[ERROR_KEY] = None
    finally:
        progress.empty()


def _render_controls(defaults) -> int:
    default_days = defaults.get("default_forecast_days", 3)
    _seed(DAYS_KEY, lambda v: v in DAY_OPTIONS, default_days)
    days = st.select_slider(
        "Forecast window (next days)", options=list(DAY_OPTIONS),
        key=DAYS_KEY, on_change=_remember, args=(DAYS_KEY,),
        help="Rolling window starting when you load the overview.",
    )
    return days


def _render_status(overview, frame, next_preferences, total) -> None:
    used = overview["preferences"]
    if used != next_preferences:
        st.info(
            f"The overview below is for the next {used.days} day(s) as "
            f"loaded on {_madrid(overview['run_at'])}. Your settings have "
            "changed; click Refresh weather overview to update it."
        )
    run_at = overview["run_at"]
    st.caption(
        f"Loaded {_madrid(run_at)} · next {used.days} day(s), until "
        f"{_madrid(run_at + used.horizon)} · daytime 09:00-18:00 "
        "Europe/Madrid (18:00 excluded)."
    )
    st.caption(f"Criteria used: {_criteria(used)}. All activities and sizes.")
    if searcher.forecast_boundary_crossed(
        overview["rows"], run_at, used.days
    ):
        st.warning(
            "This load crossed a daytime forecast-slot boundary. Some "
            "forecasts cannot cover the original window. Refresh the "
            "overview to start a new window and reuse suitable saved data."
        )
    context = search_context(frame)
    ranked = int((frame["status"] == AVAILABLE).sum()) if context else 0
    st.markdown(
        f"**{ranked} of {total} destinations can be ranked** for this "
        f"window · {overview['cached']} saved forecast(s) reused."
    )
    oldest = context["oldest_retrieved_at_utc"] if context else None
    if oldest is not None:
        st.caption(
            f"Forecasts retrieved {_madrid(oldest)} to "
            f"{_madrid(context['newest_retrieved_at_utc'])}."
        )
        if searcher.utc_now() - oldest > FORECAST_MAX_AGE:
            st.warning(
                "This overview uses forecasts retrieved over three hours "
                "ago. Click Refresh weather overview before relying on it."
            )


def _filters(catalog_rows) -> tuple:
    names = {row["city_id"]: row["city"] for row in catalog_rows}
    tags = _ordered(
        (t for row in catalog_rows for t in _activities(row["activities"])),
        ACTIVITIES,
    )
    kinds = _ordered(
        (row["destination_size"] for row in catalog_rows), DESTINATION_SIZES
    )
    first, second, third = st.columns(3)
    with first:
        chosen_ids = _multiselect(
            "Highlight destinations", FILTER_KEYS["destinations"],
            [ALL, *sorted(names, key=names.get)],
            "Highlights markers and narrows the charts; ranks stay global.",
            format_func=lambda v: v if v == ALL else names[v],
        )
    with second:
        chosen_tags = _multiselect(
            "Activities", FILTER_KEYS["activities"], [ALL, *tags],
            "Destinations offering ANY selected activity.",
        )
    with third:
        chosen_kinds = _multiselect(
            "Destination size", FILTER_KEYS["sizes"], [ALL, *kinds],
            "Destinations of ANY selected size.",
        )
    return chosen_ids, chosen_tags, chosen_kinds


def _ranking_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Weather rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Region": rows["region"],
        "Activities": rows["activities"].map(", ".join),
        "Weather score (%)": rows["weather_match_pct"],
        "Average daytime temperature (°C)": rows["mean_temperature_c"],
        "Slots with data": [
            f"{int(e)}/{int(x)}"
            for e, x in zip(
                rows["evaluated_periods"], rows["expected_periods"]
            )
        ],
    })


def _comparison_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Weather rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Average daytime temperature (°C)": rows["mean_temperature_c"],
        "Highest slot precipitation probability (%)": rows[
            "max_precipitation_probability_pct"
        ],
        "Highest slot wind speed (km/h)": rows["max_wind_kmh"],
    })


def _all_conditions_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Weather rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Slots meeting all three": rows["suitable_period_count"].astype(int),
        "Slots with data": rows["evaluated_periods"].astype(int),
        "Share of slots (%)": rows["all_preferences_pct"],
        "Temperature checks met": rows["temperature_passes"].astype(int),
        "Rain checks met": rows["precipitation_passes"].astype(int),
        "Wind checks met": rows["wind_passes"].astype(int),
    })


def _unavailable_table(rows: pd.DataFrame, errors: Mapping) -> pd.DataFrame:
    return pd.DataFrame({
        "Destination": rows["destination"],
        "Region": rows["region"],
        "Why it has no weather rank": [
            _reason(city, code, errors)
            for city, code in zip(rows["city_id"], rows["reason"])
        ],
    })


def _number_columns(labels: Iterable[str], fmt: str = "%.1f") -> dict:
    return {
        label: st.column_config.NumberColumn(label, format=fmt)
        for label in labels
    }


def _render_tabs(available: pd.DataFrame, preferences) -> None:
    ranking_tab, comparison_tab, all_tab = st.tabs(
        ["Weather ranking", "Weather comparison", "All three criteria"]
    )
    with ranking_tab:
        st.plotly_chart(weather_score_chart(available))
        st.dataframe(
            _ranking_table(available), hide_index=True,
            column_config=_number_columns(
                ["Weather score (%)", "Average daytime temperature (°C)"]
            ),
        )
        st.caption(
            "Weather score is the percentage of temperature, rain and wind "
            "checks met across the window, with no driving penalty. Equal "
            "scores share a rank. The Searcher ranks trips differently "
            f"because it subtracts a driving penalty. {SLOT_NOTE}"
        )
    with comparison_tab:
        _seed(
            METRIC_KEY,
            lambda v: v in COMPARISON_METRICS,
            next(iter(COMPARISON_METRICS)),
        )
        metric = st.radio(
            "Weather measure", list(COMPARISON_METRICS), key=METRIC_KEY,
            horizontal=True, format_func=lambda m: COMPARISON_METRICS[m][0],
            on_change=_remember, args=(METRIC_KEY,),
        )
        st.plotly_chart(comparison_chart(available, metric, preferences))
        st.caption(COMPARISON_METRICS[metric][2])
        st.dataframe(
            _comparison_table(available), hide_index=True,
            column_config=_number_columns([
                "Average daytime temperature (°C)",
                "Highest slot precipitation probability (%)",
                "Highest slot wind speed (km/h)",
            ]),
        )
    with all_tab:
        st.plotly_chart(all_preferences_chart(available))
        st.caption(
            "A slot counts only when temperature, precipitation probability "
            "and wind all meet the criteria at once. Slots are forecasts, "
            "not guaranteed good-weather hours."
        )
        st.dataframe(
            _all_conditions_table(available), hide_index=True,
            column_config=_number_columns(["Share of slots (%)"]),
        )


def render_dashboard_page() -> None:
    """Independent Dashboard: map of every destination plus weather views."""
    st.header("Dashboard")
    st.write(
        "Weather across all mainland-Spain destinations for the next few "
        "days, ranked by weather alone. Use the Searcher for a personal "
        "trip recommendation that also weighs driving time."
    )
    try:
        catalog = load_destinations()
        defaults = load_product_defaults()
    except (CatalogError, ValueError):
        st.error(
            "The destination catalog or default settings could not be "
            "loaded. Restore the project's reference files."
        )
        return
    catalog_rows = [d.as_catalog_row() for d in catalog]
    state = st.session_state

    days = _render_controls(defaults)
    next_preferences = overview_preferences(searcher.utc_now(), defaults, days)
    st.caption(
        f"Seasonal criteria for the next load: {_criteria(next_preferences)}."
        " Saved forecasts under three hours old are reused; others are "
        "fetched and saved automatically. A first full load can take a few "
        "minutes."
    )
    overview = state.get(OVERVIEW_KEY)
    if st.button(
        "Refresh weather overview" if overview else "Load weather overview",
        key=LOAD_KEY, type="primary",
    ):
        _load(catalog, defaults, days)
        # Redraw once so the button, status and map reflect the new load.
        st.rerun()

    failure = state.get(ERROR_KEY)
    if failure:
        st.error(searcher.MESSAGES.get(failure["code"], "Weather failed."))
        if failure.get("guidance"):
            st.caption(failure["guidance"])
        if overview:
            st.info("The overview below has not been refreshed.")

    frame = None
    errors = {}
    if overview:
        try:
            frame = prepare_frame(overview["rows"], catalog_rows)
        except DashboardDataError:
            st.error(
                "The loaded weather could not be displayed because it is "
                "incomplete. Click Refresh weather overview."
            )
        else:
            errors = overview["errors"]
            searcher.render_storage_failure(overview.get("storage_failure"))
            _render_status(overview, frame, next_preferences, len(catalog))
    else:
        st.info(
            f"All {len(catalog)} destinations are shown without weather. "
            "Choose the days and click Load weather overview."
        )

    chosen = _filters(catalog_rows)
    highlighted = [
        row["city_id"]
        for row in catalog_rows
        if matches(row["city_id"], _activities(row["activities"]),
                   row["destination_size"], *chosen)
    ]
    st.subheader("Mainland Spain destinations by weather score")
    st.plotly_chart(
        map_figure(map_points(catalog_rows, frame, errors), highlighted),
        # Scrolling the page over the map must not zoom it out of Spain;
        # the map's +/- buttons still zoom.
        config=MAP_CONFIG,
        alt="All 83 mainland-Spain destinations by weather-only rank",
    )
    st.caption(
        f"All {len(catalog)} destinations stay on the map. Grey markers "
        "have no weather rank yet; filters dim other markers but never "
        "change ranks. Coordinates come from the destination catalog."
    )
    if frame is None:
        return

    shown = filter_frame(frame, *chosen)
    available = shown[shown["status"] == AVAILABLE]
    unavailable = shown[shown["status"] == UNAVAILABLE]
    if shown.empty:
        st.warning(
            "No destinations match these filters. Choose All or add "
            "more options."
        )
    elif available.empty:
        st.info(
            "None of the selected destinations has a complete forecast "
            "for this window. See the reasons below."
        )
    else:
        _render_tabs(available, overview["preferences"])
    if not unavailable.empty:
        st.markdown("**Destinations without a weather rank**")
        st.caption(
            "Shown in grey on the map. They have no invented temperature, "
            "score or rank."
        )
        st.dataframe(_unavailable_table(unavailable, errors), hide_index=True)
