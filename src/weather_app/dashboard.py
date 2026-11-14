"""Independent Spain overview using seasonal comfort minus driving cost.

All destinations remain visible. Ranking uses final_score, with shared ranks
for exact ties. Every visual uses final_score, including driving; daily
heatmap cells apply the same engine to each individual day.
First entry, changed windows and manual refresh use the shared
saved-weather service. Ordinary reruns and return navigation reuse
the loaded overview; chart interactions do not fetch weather.
"""

from __future__ import annotations

import math
from html import escape
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from weather_app import searcher
from weather_app.executive import executive_summary
from weather_app.executive_view import render_kpis, render_details
from weather_app.presentation import eyebrow, duration_text, duration_column
from weather_app.scoring import wind_label
from weather_app.analytics import (
    AVAILABLE,
    destination_ranks,
    daily_weather,
    FORECAST_MAX_AGE,
    RESULT_FIELDS,
    UNAVAILABLE,
)
from weather_app.client import APIError
from weather_app.config import load_product_defaults
from weather_app.storage import CatalogError, load_destinations

MADRID = ZoneInfo("Europe/Madrid")
DAY_OPTIONS = (1, 2, 3, 4, 5)
NO_DATA_COLOUR = "#9e9e9e"
# Presentation configuration; coordinates match the documented route origin.
MADRID_ORIGIN = {"lat": 40.4168, "lon": -3.7038}
MAP_ZOOM = 4.5
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
OSM_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">'
    'OpenStreetMap contributors</a>'
)
MAP_CONFIG = {
    "scrollZoom": False, "displaylogo": False, "displayModeBar": True,
    "modeBarButtonsToAdd": ["zoomInMap", "zoomOutMap", "resetViewMap"],
}

DAYS_KEY = "dashboard_days"
LOAD_KEY = "dashboard_load"
OVERVIEW_KEY = "dashboard_overview"
ERROR_KEY = "dashboard_error"

# Scores and statistics an available row must carry as finite numbers.
_AVAILABLE_NUMBERS = RESULT_FIELDS[6:]


class DashboardDataError(ValueError):
    """Analysis or catalog rows do not match the shared P2.4 shape."""


# ---------------------------------------------------------------------------
# Criteria and ranking (pure)
# ---------------------------------------------------------------------------


def overview_preferences(now_utc: datetime, defaults: Mapping, days: int):
    """Seasonal default criteria for a Dashboard window of ``days`` days.

    Each forecast date uses its Madrid seasonal band from the reference.
    Numeric rain/wind limits remain internal diagnostic thresholds; the
    Dashboard score uses continuous comfort curves and has no city filters.
    """
    if days not in DAY_OPTIONS:
        raise ValueError("The Dashboard window must be 1-5 days.")
    bands = [None] * 12
    for season in defaults["seasonal_temperature_c"].values():
        for month in season["months"]:
            bands[month - 1] = (season["min"], season["max"])
    return replace(
        searcher.initial_preferences(now_utc, defaults), days=days,
        scoring_mode="dashboard", rain_preference=None, wind_preference=None,
        seasonal_bands=tuple(bands),
        max_precipitation_probability_pct=defaults[
            "max_precipitation_probability_percent"],
        max_wind_kmh=defaults["max_wind_kmh"],
    )


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
    """Join engine rows to the catalog and order them by Destination rank.

    ``rank`` includes the driving penalty (see ``destination_ranks``).
    Ranked rows
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

    ranks = destination_ranks(analysis_rows)
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
    return searcher.MESSAGES.get(code or "", "Forecast unavailable.")


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
            f"<b>{escape(point['city'])}</b><br>Activities: "
            f"{escape(', '.join(tags))}"
        )
        row = results.get(place["city_id"])
        if row is None:
            point["hover"] = (
                f"{heading}<br>Weather not loaded. Choose the days and "
                "click Refresh weather overview."
            )
        elif row["status"] == AVAILABLE:
            point.update(
                status="ranked",
                rank=int(row["rank"]),
                weather_score=row["final_score"],
                mean_temperature_c=row["mean_temperature_c"],
            )
            point["hover"] = (
                f"{heading}<br>Average daytime temperature: "
                f"{row['mean_temperature_c']:.1f} °C"
                f"<br>Destination rank: {point['rank']} of {ranked_total}"
                f"<br>Destination score: {row['final_score']:.1f}/100"
            )
        else:
            point["status"] = "unavailable"
            point["hover"] = (
                f"{heading}<br>No destination rank: "
                f"{_reason(place['city_id'], row['reason'], errors)}"
            )
        point["hover"] += (
            f"<br>Drive from Madrid: "
            f"{duration_text(place.get('car_duration_min'))} h one way"
        )
        points.append(point)
    return points


def map_figure(points: Sequence[Mapping]) -> go.Figure:
    """OSM tile map with all destinations plus a separate Madrid origin.

    Browser requests fetch only visible map tiles using normal caching.
    Weather remains from the validated service; OSM supplies the basemap only.
    """
    ranked = sorted((p for p in points if p["status"] == "ranked"),
                    key=lambda p: (p["rank"], p["city_id"]))
    others = sorted((p for p in points if p["status"] != "ranked"),
                    key=lambda p: p["city_id"])
    loaded = any(p["status"] != "not_loaded" for p in points)
    figure = go.Figure()
    for group, name, marker in [
        (ranked, "Destination score", {
            "size": 16, "color": [p["weather_score"] for p in ranked],
            "cmin": 0, "cmax": 100,
            "colorscale": [
                [0, "#c8463a"], [.2, "#c8463a"],
                [.2, "#ed9145"], [.4, "#ed9145"],
                [.4, "#e7c65b"], [.6, "#e7c65b"],
                [.6, "#8bb66a"], [.8, "#8bb66a"],
                [.8, "#247548"], [1, "#247548"],
            ],
            "showscale": bool(ranked),
            "colorbar": {
                "title": {"text": "Destination score /100"},
                "orientation": "h", "x": .5, "xanchor": "center",
                "y": -.06, "yanchor": "top", "len": .85,
                "thickness": 14, "outlinewidth": 0,
                "tickvals": [0, 20, 40, 60, 80, 100],
                "tickfont": {"size": 11},
            },
        }),
        (others, "No destination rank" if loaded else "Weather not loaded",
         {"size": 16, "color": NO_DATA_COLOUR}),
    ]:
        figure.add_trace(go.Scattermap(
            name=name, lat=[p["latitude"] for p in group],
            lon=[p["longitude"] for p in group],
            customdata=[p["city_id"] for p in group],
            hovertext=[p["hover"] for p in group],
            hovertemplate="%{hovertext}<extra></extra>", mode="markers",
            marker={**marker, "opacity": 0.95},
            showlegend=False,
        ))
    figure.add_trace(go.Scattermap(
        name="Madrid origin", lat=[MADRID_ORIGIN["lat"]],
        lon=[MADRID_ORIGIN["lon"]], customdata=["madrid-origin"],
        hovertext=["<b>Madrid · approximate Km0</b><br>"
                   "Fixed departure point for driving estimates.<br>"
                   "Origin marker only; not a ranked destination."],
        hovertemplate="%{hovertext}<extra></extra>", mode="markers",
        marker={"size": 23, "color": "#2489c5"}, showlegend=False,
    ))
    # Border layer underneath the circles keeps close destinations legible.
    outlines = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates":
         [p["longitude"], p["latitude"]]}, "properties": {}}
        for p in points
    ]}
    style = {
        "version": 8,
        "sources": {"osm": {
            "type": "raster", "tiles": [OSM_TILE_URL], "tileSize": 256,
            "maxzoom": 19, "attribution": OSM_ATTRIBUTION,
        }},
        "layers": [{"id": "osm-basemap", "type": "raster",
                    "source": "osm"}],
    }
    lats = [p["latitude"] for p in points] or [MADRID_ORIGIN["lat"]]
    lons = [p["longitude"] for p in points] or [MADRID_ORIGIN["lon"]]
    figure.update_layout(
        map={
            "style": style, "zoom": MAP_ZOOM,
            "center": {"lat": (min(lats) + max(lats)) / 2,
                       "lon": (min(lons) + max(lons)) / 2},
            "layers": [{"sourcetype": "geojson", "source": outlines,
                        "type": "circle", "color": "#34432c",
                        "circle": {"radius": 9}, "below": "traces"}],
        },
        height=520, margin={"l": 0, "r": 0, "t": 0, "b": 75},
        paper_bgcolor="#ffffff", font={"color": "#183535"},
        uirevision="destination-map-osm-v1",
    )
    return figure


# ---------------------------------------------------------------------------
# Streamlit rendering
# ---------------------------------------------------------------------------


def _madrid(value: datetime) -> str:
    return value.astimezone(MADRID).strftime("%a %d %b %Y, %H:%M %Z")


def _criteria(preferences):
    """Explain the active scoring mode, not obsolete pass/fail limits."""
    return (
        f"Seasonal temperature band at load: "
        f"{preferences.temperature_min_c:g}–"
        f"{preferences.temperature_max_c:g} °C; each forecast date uses "
        "its season. Gradual rain, wind and cloud components; "
        "2 points per driving hour, capped at 15"
    )


def _remember(key: str) -> None:
    """Keep a widget's value while Streamlit hides it on the Searcher."""
    st.session_state[f"_saved_{key}"] = st.session_state[key]


def _seed(key: str, valid, default) -> None:
    """Restore a widget value from its saved copy before drawing it."""
    if key in st.session_state and valid(st.session_state[key]):
        return
    saved = st.session_state.get(f"_saved_{key}")
    st.session_state[key] = saved if valid(saved) else default


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
                error.message
                if error.code in {"authentication", "storage"} else None
            ),
        }
    except ValueError:
        state[ERROR_KEY] = {"code": "invalid_input", "guidance": None}
    else:
        state[OVERVIEW_KEY] = {
            "rows": result["rows"],
            "daily": daily_weather(
                catalog, result.get("forecasts", {}), preferences, run_at
            ),
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
    days = st.selectbox(
        "Forecast window (next days)", options=list(DAY_OPTIONS),
        key=DAYS_KEY, on_change=_remember, args=(DAYS_KEY,),
        help="Rolling window starting when you load the overview.",
    )
    return days


def _render_status(overview, frame, next_preferences, total) -> None:
    used = overview["preferences"]
    if asdict(used) != asdict(next_preferences):
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
    if context is not None and oldest is not None:
        st.caption(
            f"Forecasts retrieved {_madrid(oldest)} to "
            f"{_madrid(context['newest_retrieved_at_utc'])}."
        )
        if searcher.utc_now() - oldest > FORECAST_MAX_AGE:
            st.warning(
                "This overview uses forecasts retrieved over three hours "
                "ago. Click Refresh weather overview before relying on it."
            )


def _catalogue_table(rows, catalog, errors, now):
    """Catalog facts and loaded forecast details in one sortable table."""
    places = {d.city_id: d for d in catalog}
    retrieved = pd.to_datetime(rows['forecast_retrieved_at_utc'], utc=True)
    age = (now - retrieved).dt.total_seconds().div(60).clip(lower=0)
    starts = pd.to_datetime(rows['run_at_utc'], utc=True)
    ends = starts + pd.to_timedelta(rows['days'], unit='D')
    return pd.DataFrame({
        'Destination': rows['destination'],
        'Destination score / 100': rows['final_score'],
        'Driving penalty': rows['travel_penalty'],
        'Forecast': rows['days'].map(lambda days: f'Next {days} day(s)'),
        'Temperature (°C)': rows['mean_temperature_c'],
        'Maximum rain probability (%)': (
            rows['max_precipitation_probability_pct']),
        'Maximum wind (km/h)': rows['max_wind_kmh'],
        'Wind level': rows['max_wind_kmh'].map(
            lambda v: wind_label(v) if pd.notna(v) else 'Unavailable'),
        'Activities': rows['activities'].map(' · '.join),
        'Driving distance (km)': [places[c].car_distance_km
                                  for c in rows['city_id']],
        'Driving time (h:mm)': duration_column(
            places[c].car_duration_min for c in rows['city_id']),
        'Window starts (Madrid)': starts.dt.tz_convert(MADRID),
        'Window ends (Madrid)': ends.dt.tz_convert(MADRID),
        'Retrieved (Madrid)': retrieved.dt.tz_convert(MADRID),
        'Age (h:mm)': duration_column(age),
        'Freshness': ['Unavailable' if pd.isna(a) else
                      'Over 3 hours old' if a > 180 else 'Within 3 hours'
                      for a in age],
        'Destination rank': rows['rank'].astype('Int64'),
        'Region': rows['region'],
        'Size': rows['destination_size'],
        'Slots with data': [f'{int(e)}/{int(x)}' for e, x in zip(
            rows['evaluated_periods'], rows['expected_periods'])],
        'Status': rows['status'],
        'Unavailable reason': [
            _reason(city, reason, errors) if status == UNAVAILABLE else ''
            for city, reason, status in zip(
                rows['city_id'], rows['reason'], rows['status'])],
    })


def _unavailable_table(rows: pd.DataFrame, errors: Mapping) -> pd.DataFrame:
    return pd.DataFrame({
        "Destination": rows["destination"],
        "Region": rows["region"],
        "Why it has no destination rank": [
            _reason(city, code, errors)
            for city, code in zip(rows["city_id"], rows["reason"])
        ],
    })


def _number_columns(labels: Iterable[str], fmt: str = "%.1f") -> dict:
    return {
        label: st.column_config.NumberColumn(label, format=fmt)
        for label in labels
    }


def render_dashboard_page() -> None:
    """Independent Dashboard: map of every destination plus weather views."""
    eyebrow("Destination overview")
    st.header("Dashboard")
    st.write(
        "Weather across our catalogued mainland-Spain destinations for the "
        "next few "
        "days, ranked by standard seasonal criteria and driving time. "
        "Use the Searcher for a personal "
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
        f"Current seasonal temperature band: "
        f"{next_preferences.temperature_min_c:g}–"
        f"{next_preferences.temperature_max_c:g} °C; follows each forecast "
        "date's season."
        " Saved forecasts up to three hours old are reused; others are "
        "fetched and saved automatically. The overview loads on first "
        "opening and when you change the forecast window. A first full "
        "load can take a few minutes."
    )
    overview = state.get(OVERVIEW_KEY)
    # Keep an existing snapshot on hot reload. Mark attempts before loading
    # so a failed request cannot repeat on every ordinary Streamlit rerun.
    if "dashboard_attempted_days" not in state and overview:
        state.dashboard_attempted_days = overview["preferences"].days
    refresh = st.button(
        "Refresh weather overview", key=LOAD_KEY, type="primary",
    )
    if refresh or state.get("dashboard_attempted_days") != days:
        state.dashboard_attempted_days = days
        _load(catalog, defaults, days)
        overview = state.get(OVERVIEW_KEY)

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
            "Click Refresh weather overview to retry."
        )

    summary = executive_summary(
        overview["rows"] if overview and frame is not None else [], catalog
    )
    render_kpis(summary)
    with st.container(border=True, key="map_panel"):
        st.html(
            '<div class="wi-map-heading"><h3>Destination map</h3>'
            '<span>Madrid, Spain · fixed origin for all routes</span></div>'
        )
        st.plotly_chart(
            map_figure(map_points(catalog_rows, frame, errors)),
            config=MAP_CONFIG,
            alt=f"All {len(catalog)} catalogued destinations by rank "
                "on OpenStreetMap, with Madrid as the blue origin marker",
        )
        st.caption(
            f"All {len(catalog)} destinations remain visible. "
            "Colours use fixed Destination score bands: red 0–<20, "
            "orange 20–<40, yellow 40–<60, light green 60–<80, "
            "dark green 80–100 (highly recommended). Grey means "
            "unavailable weather. Blue marks Madrid, not a ranked result. "
            "© [OpenStreetMap contributors]"
            "(https://www.openstreetmap.org/copyright)."
        )
    with st.expander("How Dashboard scores work"):
        st.write(
            "Destination score weights seasonal temperature 45%, rain 35%, "
            "wind 15% and cloud 5%. Temperature follows each forecast date's "
            "season with gradual penalties outside its ideal band. The "
            "window uses 80% average plus 20% worst-quarter weather matching. "
            "Destination score subtracts 2 points per one-way driving hour, "
            "capped at 15. All views include driving. Daily heatmap cells "
            "use each day's weather, so can differ from the window score. "
            "Scores are not probabilities or safety ratings."
        )
    if frame is None or overview is None:
        return

    shown = frame
    available = shown[shown["status"] == AVAILABLE]
    unavailable = shown.loc[shown["status"] == UNAVAILABLE, :]
    if shown.empty:
        st.warning(
            "No destination results were loaded. Refresh the overview "
            "to try again."
        )
    elif available.empty:
        st.info(
            "None of the catalogued destinations has a complete forecast "
            "for this window. See the reasons below."
        )
    else:
        render_details(summary, overview.get("daily", []), catalog)
    with st.expander(f"All {len(catalog)} destinations"):
        full = _catalogue_table(
            frame, catalog, errors, searcher.utc_now()
        )
        st.caption(
            "Sortable catalogue · click a column header to sort. "
            "Temperature is the daytime mean; rain and wind are the "
            "highest daytime-slot values across the selected window. "
            "Scroll right for driving details, dates and freshness. "
            "Missing weather stays blank, never zero."
        )
        columns = _number_columns([
            "Temperature (°C)", "Maximum rain probability (%)",
            "Maximum wind (km/h)",
            "Driving distance (km)",
        ])
        columns["Destination score / 100"] = st.column_config.NumberColumn(
            "Destination score", format="%.1f/100"
        )
        columns["Destination"] = st.column_config.TextColumn(
            "Destination", pinned=True, width="medium"
        )
        columns["Activities"] = st.column_config.TextColumn(
            "Activities", width="large"
        )
        for label in ["Window starts (Madrid)", "Window ends (Madrid)",
                      "Retrieved (Madrid)"]:
            columns[label] = st.column_config.DatetimeColumn(
                label, format="DD MMM YYYY HH:mm"
            )
        st.dataframe(
            full, hide_index=True, width="stretch", height=560,
            row_height=34, column_config=columns,
            alt=f"All {len(catalog)} destinations with weather, "
                "activities, "
                "driving estimates, forecast dates and freshness",
        )
    if not unavailable.empty:
        st.markdown("**Destinations without a destination rank**")
        st.caption(
            "Shown in grey on the map. They have no invented temperature, "
            "score or rank."
        )
        st.dataframe(_unavailable_table(unavailable, errors), hide_index=True)
