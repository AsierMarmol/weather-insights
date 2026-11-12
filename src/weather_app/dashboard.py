"""P4.2 Dashboard: interactive views of the shared search results.

The Dashboard only *presents* rows produced by the shared analytics engine
(``analytics.analyse_destinations``) for the Searcher's last search. It never
calls the weather service, never recalculates scores and never re-sorts the
ranking: the order of ``analysis_rows`` is the agreed ranking
(PHASE2_SCOPE.md, P2.4).

Entry points:

* ``render_dashboard(analysis_rows, catalog_rows)`` - the P2.4 contract.
  ``catalog_rows`` are ``Destination.as_catalog_row()`` dictionaries.
* ``render_dashboard_page()`` - reads the shared ``search_*`` session state
  written by the Searcher and loads the catalog, for the app's navigation.

Dashboard filters live under their own ``dashboard_*`` session keys, so
narrowing the view never changes the shared ``search_*`` state.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
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
from weather_app.models import ACTIVITIES, DESTINATION_SIZES
from weather_app.storage import CatalogError, load_destinations

MADRID = ZoneInfo("Europe/Madrid")
ALL = "All"

# Scores and statistics an available row must carry as finite numbers.
_AVAILABLE_NUMBERS = RESULT_FIELDS[6:]

# Weather comparison metrics: (chart title, axis label, aggregation note).
COMPARISON_METRICS = {
    "mean_temperature_c": (
        "Mean daytime temperature",
        "Mean temperature (°C)",
        "Average temperature over every evaluated 3-hour daytime "
        "forecast period.",
    ),
    "max_precipitation_probability_pct": (
        "Highest precipitation probability",
        "Highest period precipitation probability (%)",
        "Highest probability in any single 3-hour daytime period. "
        "It is not the probability of rain over the whole trip.",
    ),
    "max_wind_kmh": (
        "Strongest daytime wind",
        "Highest period wind speed (km/h)",
        "Highest sustained wind speed (not gusts) in any single 3-hour "
        "daytime period.",
    ),
}

FILTER_KEYS = {
    "destinations": "dashboard_destinations",
    "activities": "dashboard_activities",
    "sizes": "dashboard_sizes",
}
METRIC_KEY = "dashboard_metric"


class DashboardDataError(ValueError):
    """Analysis or catalog rows do not match the shared P2.4 shape."""


# ---------------------------------------------------------------------------
# Pure data helpers
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


def _check_row(position: int, row: Mapping) -> int | None:
    """Validate one result row; return 1 for available, None otherwise."""
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
        return 1
    if row["status"] == UNAVAILABLE:
        if not row["reason"]:
            raise DashboardDataError(
                f"unavailable row {city_id} has no reason"
            )
        return None
    raise DashboardDataError(
        f"unknown status {row['status']!r} for {city_id}"
    )


def prepare_frame(
    analysis_rows: Sequence[Mapping], catalog_rows: Sequence[Mapping]
) -> pd.DataFrame:
    """Join results to canonical catalog fields, keeping the given order.

    ``rank`` is the 1-based position among available rows in the shared
    ranking, so it matches the Searcher even after Dashboard filters hide
    rows. Raises ``DashboardDataError`` for rows outside the contract.
    """
    catalog = {}
    for place in catalog_rows:
        if not place.get("city_id"):
            raise DashboardDataError("catalog row without city_id")
        catalog[place["city_id"]] = place

    records, searches, seen, rank = [], set(), set(), 0
    for position, row in enumerate(analysis_rows):
        counts = _check_row(position, row)
        city_id = row["city_id"]
        if city_id not in catalog:
            raise DashboardDataError(
                f"result city {city_id!r} is not in the catalog"
            )
        if city_id in seen:
            raise DashboardDataError(f"result city {city_id!r} repeats")
        seen.add(city_id)
        rank += counts or 0
        run_at = _parse_utc("run_at_utc", row["run_at_utc"])
        searches.add((run_at, row["days"]))
        retrieved = row["forecast_retrieved_at_utc"]
        place = catalog[city_id]
        record = {name: row[name] for name in RESULT_FIELDS}
        record.update(
            rank=rank if counts else None,
            destination=place["city"],
            region=place.get("region", ""),
            activities=_activities(place.get("activities", ())),
            destination_size=place.get("destination_size", ""),
            car_distance_km=float(place["car_distance_km"]),
            car_duration_min=float(place["car_duration_min"]),
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
    columns = [
        "rank", "destination", "region", "activities", "destination_size",
        "car_distance_km", "car_duration_min", *RESULT_FIELDS,
    ]
    frame = pd.DataFrame.from_records(records, columns=columns)
    frame["rank"] = frame["rank"].astype("Int64")  # <NA> when unavailable
    return frame


def _clean(selection: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(item for item in (selection or ()) if item != ALL)


def filter_frame(
    frame: pd.DataFrame,
    destinations: Iterable[str] | None = None,
    activities: Iterable[str] | None = None,
    sizes: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Keep rows matching ANY chosen value per group; AND between groups.

    An empty selection (or only ``All``) means no restriction. Destinations
    are matched by ``city_id``. Row order is preserved.
    """
    ids, tags, kinds = _clean(destinations), _clean(activities), _clean(sizes)
    mask = pd.Series(True, index=frame.index)
    if ids:
        mask &= frame["city_id"].isin(ids)
    if tags:
        wanted = set(tags)
        mask &= frame["activities"].map(lambda t: bool(wanted.intersection(t)))
    if kinds:
        mask &= frame["destination_size"].isin(kinds)
    return frame[mask]


def search_context(frame: pd.DataFrame) -> dict | None:
    """Shared search time, forecast window and retrieval times."""
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


def _available(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame["status"] == AVAILABLE]


def _labels(rows: pd.DataFrame) -> list[str]:
    return [f"{r}. {n}" for r, n in zip(rows["rank"], rows["destination"])]


def _bar_layout(figure: go.Figure, title: str, axis: str, rows: int) -> None:
    figure.update_layout(
        title=title,
        xaxis_title=axis,
        yaxis_title="Destination (shared rank)",
        yaxis_autorange="reversed",
        height=max(260, 90 + 26 * rows),
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )


def ranking_chart(frame: pd.DataFrame) -> go.Figure:
    """Final score per destination in shared ranking order (best on top)."""
    rows = _available(frame)
    figure = go.Figure(
        go.Bar(
            x=rows["final_score"].tolist(),
            y=_labels(rows),
            orientation="h",
            customdata=list(
                zip(
                    rows["weather_match_pct"],
                    rows["travel_penalty"],
                    rows["car_duration_min"],
                )
            ),
            hovertemplate=(
                "%{y}<br>Final score: %{x:.1f} points"
                "<br>Weather match: %{customdata[0]:.1f}%"
                "<br>Driving penalty: −%{customdata[1]:.2f} points"
                "<br>Drive from Madrid: %{customdata[2]:.0f} min"
                "<extra></extra>"
            ),
        )
    )
    _bar_layout(
        figure,
        "Suitability ranking: final score by destination",
        "Final score (points, 0-100) = weather match % − driving penalty "
        "(max 5)",
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
    if low is not None and high is not None:
        figure.add_vrect(
            x0=low, x1=high, fillcolor="green", opacity=0.12, line_width=0,
            annotation_text="Your range", annotation_position="top left",
        )
    elif high is not None:
        figure.add_vline(
            x=high, line_dash="dash", annotation_text="Your limit",
            annotation_position="top right",
        )
    _bar_layout(figure, f"{title} across destinations", axis, len(rows))
    return figure


def all_preferences_chart(frame: pd.DataFrame) -> go.Figure:
    """Share of evaluated periods meeting all three preferences at once."""
    rows = _available(frame)
    counts = [
        f"{int(ok)}/{int(total)} periods"
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
                "%{y}<br>%{x:.1f}% of periods (%{text})<extra></extra>"
            ),
        )
    )
    _bar_layout(
        figure,
        "Daytime forecast periods meeting all three preferences",
        "Periods meeting temperature, rain and wind limits together (%)",
        len(rows),
    )
    figure.update_xaxes(range=[0, 100])
    return figure


# ---------------------------------------------------------------------------
# Streamlit rendering
# ---------------------------------------------------------------------------


def _madrid(value: datetime) -> str:
    return value.astimezone(MADRID).strftime("%a %d %b %Y, %H:%M %Z")


def _duration(minutes: float) -> str:
    hours, mins = divmod(int(round(minutes)), 60)
    return f"{hours} h {mins:02d} min"


def _age(delta: timedelta) -> str:
    minutes = int(delta.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d} min"


def _keep_all_exclusive(key: str) -> None:
    """A specific value clears All; choosing All (or nothing) restores it.

    The choice is also copied to a plain session key, because Streamlit
    discards widget state while the Searcher is shown.
    """
    st.session_state[key] = searcher.normalize_all_selection(
        st.session_state.get(key, [])
    )
    st.session_state[f"_saved{key}"] = list(st.session_state[key])


def _multiselect(label, key, options, help_text, format_func=str):
    stored = st.session_state.get(key) or st.session_state.get(f"_saved{key}")
    if not stored or any(item not in options for item in stored):
        stored = [ALL]
    st.session_state[key] = stored
    return st.multiselect(
        label, options, key=key, format_func=format_func,
        on_change=_keep_all_exclusive, args=(key,), help=help_text,
    )


def _ordered(values: Iterable[str], canonical: Sequence[str]) -> list[str]:
    present = set(values)
    extra = sorted(present - set(canonical))
    return [v for v in canonical if v in present] + extra


def _render_context(frame: pd.DataFrame, preferences: object) -> None:
    context = search_context(frame)
    st.caption(
        f"Search run {_madrid(context['run_at_utc'])} · next "
        f"{context['days']} day(s), until "
        f"{_madrid(context['window_end_utc'])} · daytime periods "
        "09:00-18:00 Europe/Madrid (18:00 excluded)."
    )
    oldest = context["oldest_retrieved_at_utc"]
    if oldest is not None:
        st.caption(
            f"Forecasts retrieved {_madrid(oldest)} to "
            f"{_madrid(context['newest_retrieved_at_utc'])}; the oldest "
            f"was {_age(context['oldest_age'])} old at search time."
        )
        if searcher.utc_now() - oldest > FORECAST_MAX_AGE:
            st.warning(
                "These results use forecasts retrieved over three hours "
                "ago. Search again in the Searcher before choosing."
            )
    if preferences is not None:
        try:
            st.caption(
                f"Preferences used: {preferences.temperature_min_c:g}-"
                f"{preferences.temperature_max_c:g} °C · precipitation "
                "probability ≤ "
                f"{preferences.max_precipitation_probability_pct:g}% · "
                f"wind ≤ {preferences.max_wind_kmh:g} km/h."
            )
        except (AttributeError, TypeError, ValueError):
            pass


def _ranking_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Region": rows["region"],
        "Final score (points)": rows["final_score"],
        "Weather match (%)": rows["weather_match_pct"],
        "Driving penalty (points)": rows["travel_penalty"],
        "Drive from Madrid": rows["car_duration_min"].map(_duration),
        "Distance (km)": rows["car_distance_km"],
    })


def _comparison_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Mean temperature (°C)": rows["mean_temperature_c"],
        "Highest precipitation probability (%)": rows[
            "max_precipitation_probability_pct"
        ],
        "Highest wind speed (km/h)": rows["max_wind_kmh"],
        "Periods evaluated": rows["evaluated_periods"].astype(int),
    })


def _all_preferences_table(rows: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Rank": rows["rank"].astype(int),
        "Destination": rows["destination"],
        "Periods meeting all": rows["suitable_period_count"].astype(int),
        "Periods evaluated": rows["evaluated_periods"].astype(int),
        "Share of periods (%)": rows["all_preferences_pct"],
        "Temperature checks passed": rows["temperature_passes"].astype(int),
        "Rain checks passed": rows["precipitation_passes"].astype(int),
        "Wind checks passed": rows["wind_passes"].astype(int),
    })


def _unavailable_table(rows: pd.DataFrame, errors: Mapping) -> pd.DataFrame:
    def reason(row):
        code = errors.get(row["city_id"], row["reason"])
        return searcher.MESSAGES.get(code, "Forecast unavailable.")

    return pd.DataFrame({
        "Destination": rows["destination"],
        "Region": rows["region"],
        "Why it is unavailable": rows.apply(reason, axis=1),
        "Daytime periods expected": rows["expected_periods"],
    })


def _number_columns(labels: Iterable[str], fmt: str = "%.1f") -> dict:
    return {
        label: st.column_config.NumberColumn(label, format=fmt)
        for label in labels
    }


def _filters(frame: pd.DataFrame) -> pd.DataFrame:
    names = dict(zip(frame["city_id"], frame["destination"]))
    tags = _ordered(
        (tag for row in frame["activities"] for tag in row), ACTIVITIES
    )
    kinds = _ordered(frame["destination_size"], DESTINATION_SIZES)
    first, second, third = st.columns(3)
    with first:
        chosen_ids = _multiselect(
            "Destinations", FILTER_KEYS["destinations"],
            [ALL, *sorted(names, key=names.get)],
            "Compare only the destinations you choose.",
            format_func=lambda v: v if v == ALL else names[v],
        )
    with second:
        chosen_tags = _multiselect(
            "Activities", FILTER_KEYS["activities"], [ALL, *tags],
            "Shows destinations offering ANY selected activity.",
        )
    with third:
        chosen_kinds = _multiselect(
            "Destination size", FILTER_KEYS["sizes"], [ALL, *kinds],
            "Shows destinations of ANY selected size.",
        )
    return filter_frame(frame, chosen_ids, chosen_tags, chosen_kinds)


def _remember_metric() -> None:
    """Preserve the chart choice when Streamlit removes hidden widgets."""
    st.session_state["_saved_dashboard_metric"] = st.session_state[METRIC_KEY]


def _render_tabs(available: pd.DataFrame, preferences: object) -> None:
    ranking_tab, comparison_tab, all_tab = st.tabs(
        ["Ranking", "Weather comparison", "Periods meeting all preferences"]
    )
    with ranking_tab:
        st.plotly_chart(ranking_chart(available))
        st.dataframe(
            _ranking_table(available), hide_index=True,
            column_config={
                **_number_columns(
                    ["Final score (points)", "Weather match (%)"]
                ),
                **_number_columns(["Driving penalty (points)"], "%.2f"),
                **_number_columns(["Distance (km)"], "%.0f"),
            },
        )
        st.caption(
            "Rank is the shared position from the search, as in the "
            "Searcher. Driving times are reference estimates from Madrid."
        )
    with comparison_tab:
        if METRIC_KEY not in st.session_state:
            saved = st.session_state.get("_saved_dashboard_metric")
            st.session_state[METRIC_KEY] = (
                saved if saved in COMPARISON_METRICS
                else next(iter(COMPARISON_METRICS))
            )
        metric = st.radio(
            "Weather measure", list(COMPARISON_METRICS), key=METRIC_KEY,
            horizontal=True, format_func=lambda m: COMPARISON_METRICS[m][0],
            on_change=_remember_metric,
        )
        st.plotly_chart(comparison_chart(available, metric, preferences))
        st.caption(COMPARISON_METRICS[metric][2])
        st.dataframe(
            _comparison_table(available), hide_index=True,
            column_config=_number_columns([
                "Mean temperature (°C)",
                "Highest precipitation probability (%)",
                "Highest wind speed (km/h)",
            ]),
        )
    with all_tab:
        st.plotly_chart(all_preferences_chart(available))
        st.caption(
            "A period counts only when temperature, precipitation "
            "probability and wind all meet your preferences at once. "
            "Periods are 3-hour forecast steps, not guaranteed "
            "good-weather hours."
        )
        st.dataframe(
            _all_preferences_table(available), hide_index=True,
            column_config=_number_columns(["Share of periods (%)"]),
        )


def render_dashboard(
    analysis_rows: Sequence[Mapping], catalog_rows: Sequence[Mapping]
) -> None:
    """Render ranking, weather comparison and all-preferences views."""
    if not analysis_rows:
        st.info(
            "No destinations to show. Run a search in the Searcher with "
            "broader activity or size choices."
        )
        return
    try:
        frame = prepare_frame(analysis_rows, catalog_rows)
    except DashboardDataError:
        st.error(
            "The search results could not be displayed because they are "
            "incomplete. Run the search again in the Searcher."
        )
        return

    state = st.session_state
    preferences = state.get("search_result_preferences")
    current = state.get("search_preferences")
    if None not in (preferences, current) and preferences != current:
        st.info(
            "Your settings changed after this search. The dashboard shows "
            "the last search; search again to update it."
        )
    _render_context(frame, preferences)

    shown = _filters(frame)
    if shown.empty:
        st.warning(
            "No destinations match these dashboard filters. Choose All or "
            "add more options."
        )
        return
    available = _available(shown)
    unavailable = shown[shown["status"] == UNAVAILABLE]
    st.caption(
        f"Showing {len(available)} ranked and {len(unavailable)} "
        "unavailable destination(s)."
    )
    if available.empty:
        st.info(
            "None of the selected destinations has a complete forecast to "
            "chart. See the reasons below."
        )
    else:
        _render_tabs(available, preferences)
    if not unavailable.empty:
        st.markdown("**Unavailable destinations**")
        st.caption("These are not ranked and are not counted as zero scores.")
        st.dataframe(
            _unavailable_table(unavailable, state.get("search_errors", {})),
            hide_index=True,
        )


def render_dashboard_page() -> None:
    """Dashboard view over the Searcher's last results (shared state)."""
    st.header("Dashboard")
    st.write(
        "Compare the destinations from your last search: ranking, weather "
        "and how much of the trip meets all your preferences."
    )
    if "search_analysis_rows" not in st.session_state:
        st.info(
            "No search yet. Open the Searcher, choose your preferences and "
            "click Search destinations; the results appear here too."
        )
        return
    try:
        catalog = [d.as_catalog_row() for d in load_destinations()]
    except CatalogError:
        st.error(
            "The destination catalog could not be loaded. Restore the "
            "project's reference files."
        )
        return
    render_dashboard(st.session_state.search_analysis_rows, catalog)
