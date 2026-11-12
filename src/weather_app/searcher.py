"""P4.1 trip search over the shared weather service and analytical engine."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

from weather_app.analytics import (
    analyse_destinations,
    forecasts_from_service,
    is_eligible,
)
from weather_app.client import APIError
from weather_app.config import load_product_defaults
from weather_app.models import SearchPreferences
from weather_app.service import WeatherService
from weather_app.storage import CatalogError, load_destinations

MADRID = ZoneInfo("Europe/Madrid")
MESSAGES = {
    "authentication": "Check your local API key; it is missing or rejected.",
    "location_not_found": "The weather provider could not find this place.",
    "rate_limited": "The request limit was reached. Wait before searching.",
    "network": "Connection failed. Check your internet and try again.",
    "provider": "The weather provider is unavailable. Try again later.",
    "invalid_input": "The request contains invalid settings.",
    "invalid_data": "The weather response could not be validated.",
    "storage": (
        "Weather could not be saved or read. Check the local data file."
    ),
    "fetch_failed": "No usable forecast was returned.",
    "stale_forecast": "The forecast is too old for this search.",
    "duplicate_periods": "The forecast contains conflicting periods.",
    "missing_periods": "The forecast does not cover the full selected window.",
    "missing_metrics": "Required weather measurements are missing.",
}
WIDGETS = {
    "_trip_days": "days",
    "_trip_min": "temperature_min_c",
    "_trip_max": "temperature_max_c",
    "_trip_rain": "max_precipitation_probability_pct",
    "_trip_wind": "max_wind_kmh",
    "_trip_activities": "activities",
    "_trip_sizes": "destination_sizes",
}


def utc_now():
    """One aware time source, replaceable in offline interface tests."""
    return datetime.now(timezone.utc)


def initial_preferences(now_utc, defaults):
    """Use the Madrid season only on first use or explicit reset."""
    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ValueError("Initial preferences need an aware datetime.")
    month = now_utc.astimezone(MADRID).month
    season = next(
        s
        for s in defaults["seasonal_temperature_c"].values()
        if month in s["months"]
    )
    return SearchPreferences(
        days=defaults["default_forecast_days"],
        temperature_min_c=season["min"],
        temperature_max_c=season["max"],
        max_precipitation_probability_pct=(
            defaults["max_precipitation_probability_percent"]
        ),
        max_wind_kmh=defaults["max_wind_kmh"],
    )


def get_service():
    """Create one service per app session, lazily after a search request."""
    if "weather_service" not in st.session_state:
        st.session_state.weather_service = WeatherService.from_environment()
    return st.session_state.weather_service


def search_destinations(catalog, preferences, service, run_at, progress=None):
    """Filter before fetching; reuse the production save and scoring paths."""
    eligible = [d for d in catalog if is_eligible(d, preferences)]
    if not eligible:
        return {"rows": [], "errors": {}, "cached": 0, "eligible": 0}
    results = service.forecast_many(eligible, on_progress=progress)
    rows = analyse_destinations(
        eligible, forecasts_from_service(results), preferences, run_at
    )
    # A cached forecast may have lost its fifth-day coverage as time moved on.
    # Refresh only those cached groups once, using the same service/save path.
    refresh_ids = {
        r["city_id"]
        for r in rows
        if r["reason"] in {"missing_periods", "stale_forecast"}
        and results[r["city_id"]]["from_cache"]
    }
    if refresh_ids:
        refreshed = service.forecast_many(
            [d for d in eligible if d.city_id in refresh_ids],
            force_refresh=True,
            on_progress=progress,
        )
        results.update(refreshed)
        rows = analyse_destinations(
            eligible, forecasts_from_service(results), preferences, run_at
        )
    return {
        "rows": rows,
        "errors": {
            city: result["error"]["code"]
            for city, result in results.items()
            if result["error"]
        },
        "cached": sum(r["from_cache"] for r in results.values()),
        "eligible": len(eligible),
    }


def _seed_widgets(preferences, overwrite=False):
    for key, field in WIDGETS.items():
        if overwrite or key not in st.session_state:
            value = getattr(preferences, field)
            if field in {"activities", "destination_sizes"}:
                value = list(value) or ["All"]
            st.session_state[key] = value


def _reset(defaults):
    preferences = initial_preferences(utc_now(), defaults)
    st.session_state.search_preferences = preferences
    _seed_widgets(preferences, overwrite=True)


def _selection(values):
    return () if not values or "All" in values else tuple(values)


def _controls(catalog, defaults):
    st.button(
        "Reset to seasonal defaults",
        key="reset_preferences",
        on_click=_reset,
        args=(defaults,),
    )
    _seed_widgets(st.session_state.search_preferences)
    with st.container(border=True):
        st.subheader("Plan your trip")
        st.select_slider(
            "Forecast window (days from now)",
            options=[1, 2, 3, 4, 5],
            key="_trip_days",
        )
        left, right = st.columns(2)
        with left:
            st.number_input(
                "Minimum comfortable temperature (°C)",
                step=1.0,
                key="_trip_min",
            )
            st.number_input(
                "Maximum precipitation probability (%)",
                min_value=0.0,
                max_value=100.0,
                step=5.0,
                key="_trip_rain",
            )
        with right:
            st.number_input(
                "Maximum comfortable temperature (°C)",
                step=1.0,
                key="_trip_max",
            )
            st.number_input(
                "Maximum wind (km/h)",
                min_value=0.0,
                step=5.0,
                key="_trip_wind",
            )
        st.multiselect(
            "Activities",
            ["All"] + sorted({tag for d in catalog for tag in d.activities}),
            key="_trip_activities",
            help="Remove All to choose specific activities. Empty means All.",
        )
        st.multiselect(
            "Destination size",
            ["All"] + sorted({d.destination_size for d in catalog}),
            key="_trip_sizes",
            help="Remove All to choose specific sizes. Empty means All.",
        )
        if not st.session_state._trip_activities:
            st.caption("Activities: All")
        if not st.session_state._trip_sizes:
            st.caption("Destination size: All")
    try:
        preferences = SearchPreferences(
            **{
                field: (
                    _selection(st.session_state[key])
                    if field in {"activities", "destination_sizes"}
                    else st.session_state[key]
                )
                for key, field in WIDGETS.items()
            }
        )
    except ValueError:
        st.error(
            "Check your settings: minimum temperature cannot exceed "
            "maximum, and probability/wind limits must be valid."
        )
        return None
    st.session_state.search_preferences = preferences
    return preferences


def ranking_table(rows, catalog, errors):
    """Presentation only: preserve engine order and label units/reasons."""
    places = {d.city_id: d for d in catalog}
    table = []
    for row in rows:
        d = places[row["city_id"]]
        reason = errors.get(d.city_id, row["reason"])
        table.append(
            {
                "City": d.city,
                "Region": d.region,
                "Status": (
                    "Available"
                    if row["status"] == "available"
                    else MESSAGES.get(reason, "Forecast unavailable.")
                ),
                "Score / 100": row["final_score"],
                "Weather match (%)": row["weather_match_pct"],
                "All preferences (%)": row["all_preferences_pct"],
                "Drive (min)": d.car_duration_min,
                "Distance (km)": d.car_distance_km,
                "Daytime periods": row["evaluated_periods"],
                "Expected periods": row["expected_periods"],
                "Forecast retrieved (UTC)": row["forecast_retrieved_at_utc"],
            }
        )
    return table


def _render_results(catalog, current_preferences, defaults):
    if "search_analysis_rows" not in st.session_state:
        st.info("Choose your preferences, then search for a weather match.")
        return
    state = st.session_state
    rows = state.search_analysis_rows
    searched = state.search_result_preferences
    if current_preferences != searched:
        st.info(
            "Settings changed. Results below use your last search. "
            "Click Search destinations to update them."
        )
    run_at = state.search_run_at_utc
    end = run_at + searched.horizon
    start_label = run_at.astimezone(MADRID).strftime("%d %b %Y, %H:%M %Z")
    end_label = end.astimezone(MADRID).strftime("%d %b %Y, %H:%M %Z")
    st.subheader("Your results")
    st.caption(
        f"{start_label} → {end_label}. Madrid daytime: 09:00–18:00 "
        "(18:00 excluded), using three-hour forecast periods."
    )
    st.caption(
        f"Preferences: {searched.temperature_min_c:g}–"
        f"{searched.temperature_max_c:g} °C · rain probability ≤"
        f"{searched.max_precipitation_probability_pct:g}% · wind ≤"
        f"{searched.max_wind_kmh:g} km/h. Activities: "
        f"{', '.join(searched.activities) or 'All'}. Size: "
        f"{', '.join(searched.destination_sizes) or 'All'}."
    )
    if not rows:
        st.warning(
            "No destinations match these activity and size filters. "
            "Try All or broaden your selection."
        )
        return
    available = [r for r in rows if r["status"] == "available"]
    st.caption(
        f"{len(available)} available · "
        f"{len(rows) - len(available)} unavailable · "
        f"{state.search_cached_count} reused saved forecasts."
    )
    receipt_times = [
        datetime.fromisoformat(r["forecast_retrieved_at_utc"])
        for r in rows
        if r["forecast_retrieved_at_utc"]
    ]
    if receipt_times:
        oldest_age = max(
            0, (utc_now() - min(receipt_times)).total_seconds() / 60
        )
        st.caption(f"Oldest forecast was retrieved {oldest_age:.0f} min ago.")
        if oldest_age > 180:
            st.warning(
                "These saved results are now over three hours old. "
                "Search again before choosing a destination."
            )
    table = ranking_table(rows, catalog, state.search_errors)
    places = {d.city_id: d for d in catalog}
    if available:
        st.subheader("Top recommendations")
        for rank, row in enumerate(
            available[: defaults["recommendation_count"]], start=1
        ):
            d = places[row["city_id"]]
            with st.container(border=True):
                st.markdown(f"**{rank}. {d.city} · {d.region}**")
                st.caption(
                    f"{d.car_distance_km:g} km · "
                    f"{d.car_duration_min:g} min one-way drive"
                )
                score, match, suitable = st.columns(3)
                score.metric("Trip score / 100", f"{row['final_score']:.1f}")
                match.metric(
                    "Weather match", f"{row['weather_match_pct']:.1f}%"
                )
                suitable.metric(
                    "All preferences met", f"{row['all_preferences_pct']:.1f}%"
                )
                st.caption(
                    f"{row['evaluated_periods']}/{row['expected_periods']} "
                    "daytime periods covered · "
                    f"{row['travel_penalty']:.2f} driving penalty points"
                )
    else:
        st.warning(
            "No complete usable forecasts for this search. "
            "See each destination's reason below."
        )
    st.subheader("Full ranking")
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        alt="All eligible destinations ranked by weather and driving time",
        column_config={
            label: st.column_config.NumberColumn(label, format="%.1f")
            for label in [
                "Score / 100",
                "Weather match (%)",
                "All preferences (%)",
            ]
        },
    )
    with st.expander("How the ranking works"):
        st.write(
            "Each daytime period earns one point for temperature in your "
            "range, one for precipitation probability below your limit, and "
            "one for wind below your limit (boundaries included). Weather "
            "match is the percentage of checks passed. The trip score "
            "subtracts one point per driving hour, capped at five, with a "
            "minimum score of zero. All preferences met is the percentage "
            "of periods passing all three checks together; it adds no "
            "extra points. Activities and size only filter destinations."
        )
        st.caption(
            "Driving times are reference estimates from Madrid Km0, not "
            "live traffic. Forecasts are predictions, not guaranteed "
            "good-weather hours. Source: OpenWeather."
        )


def render_searcher():
    """Render controls first; network work happens only on explicit search."""
    st.header("Searcher")
    st.write(
        "Find a mainland-Spain car trip from Madrid that fits your weather."
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
    if "search_preferences" not in st.session_state:
        st.session_state.search_preferences = initial_preferences(
            utc_now(), defaults
        )
    preferences = _controls(catalog, defaults)
    eligible_count = (
        sum(is_eligible(d, preferences) for d in catalog) if preferences else 0
    )
    st.caption(
        f"{eligible_count} matching destinations. New forecasts save "
        "automatically; saved forecasts are reused when suitable. "
        "A full search can take a few minutes."
    )
    if st.button(
        "Search destinations",
        type="primary",
        key="run_search",
        disabled=preferences is None,
    ):
        run_at = utc_now()
        progress = st.progress(0.0, text="Preparing your search…")
        names = {d.city_id: d.city for d in catalog}

        def update(done, total, city_id, result):
            progress.progress(
                done / total, text=f"{done}/{total} · {names[city_id]}"
            )

        try:
            service = get_service() if eligible_count else None
            result = search_destinations(
                catalog, preferences, service, run_at, update
            )
        except APIError as error:
            st.error(MESSAGES.get(error.code, "Weather is unavailable."))
            st.info("Previous results, if shown, have not been refreshed.")
        except ValueError:
            st.error(
                "Weather configuration is invalid. Check the local "
                "reference settings before searching again."
            )
        else:
            state = st.session_state
            state.search_run_at_utc = run_at
            state.search_analysis_rows = result["rows"]
            state.search_result_preferences = preferences
            state.search_errors = result["errors"]
            state.search_cached_count = result["cached"]
            for code in sorted(set(result["errors"].values())):
                st.warning(MESSAGES.get(code, "Weather is unavailable."))
        finally:
            progress.empty()
    _render_results(catalog, preferences, defaults)
