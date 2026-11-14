"""P4.1 trip search over the shared weather service and analytical engine."""

from dataclasses import asdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

from weather_app.analytics import (
    analyse_destinations,
    forecasts_from_service,
    expected_period_times,
    is_eligible,
)
from weather_app.client import APIError
from weather_app.config import load_product_defaults, seasonal_defaults
from weather_app.presentation import (
    eyebrow, recommendation_cards, duration_text, duration_column,
)
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
    "duplicate_periods": "The forecast repeats a three-hour slot.",
    "missing_periods": (
        "The forecast does not cover every three-hour daytime slot in "
        "the selected window."
    ),
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


# Numeric widget codes for preferred bands, not maximum tolerances.
RAIN_CHOICES = {
    30.0: "Low (0–30%)",
    60.0: "Medium (>30–60%)",
    100.0: "High (>60–100%)",
}
WIND_CHOICES = {
    19.0: "Gentle (<20 km/h)",
    28.0: "Moderate (20–<29 km/h)",
    38.0: "Fresh (29–<39 km/h)",
    49.0: "Strong (39–<50 km/h)",
}
CATEGORY_WIDGETS = {"_trip_rain": RAIN_CHOICES, "_trip_wind": WIND_CHOICES}


def preferred_label(category, choices, maximum, unit):
    """Use saved category labels; support legacy numeric callers explicitly."""
    if category:
        return next(label for label in choices.values()
                    if label.startswith(category + " ("))
    return f"0–{maximum:g}{unit}"


def category_limit(value, choices):
    """Map a prior numeric preference to the nearest accepting preset."""
    return next((limit for limit in choices if value <= limit), max(choices))


def utc_now():
    """One aware time source, replaceable in offline interface tests."""
    return datetime.now(timezone.utc)


def initial_preferences(now_utc, defaults):
    """Use the Madrid season only on first use or explicit reset."""
    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ValueError("Initial preferences need an aware datetime.")
    _, season = seasonal_defaults(now_utc, defaults)
    rain = category_limit(
        defaults["max_precipitation_probability_percent"], RAIN_CHOICES
    )
    wind = category_limit(defaults["max_wind_kmh"], WIND_CHOICES)
    return SearchPreferences(
        rain_preference=RAIN_CHOICES[rain].split()[0],
        wind_preference=WIND_CHOICES[wind].split()[0],
        days=defaults["default_forecast_days"],
        temperature_min_c=season["min"],
        temperature_max_c=season["max"],
        max_precipitation_probability_pct=rain,
        max_wind_kmh=wind,
    )


class PendingServiceReloadError(APIError):
    """Keep an obsolete service alive until its fetched records are saved."""

    code = "storage"


def get_service():
    """Reuse the session service unless a code reload replaced its class."""
    service = st.session_state.get("weather_service")
    if service is not None and not isinstance(service, WeatherService):
        # Streamlit keeps session objects when it reloads Python modules.
        # Old class identities reject newly loaded Destination objects.
        if service.unsaved_record_count:
            service.retry_unsaved()
            if service.unsaved_record_count:
                raise PendingServiceReloadError(
                    "The app was updated, but fetched weather is still "
                    "waiting to be saved. Keep this tab open, fix the local "
                    "data-file issue, then retry. No records were discarded."
                )
        service = None
    if service is None:
        service = WeatherService.from_environment()
        st.session_state.weather_service = service
    return service


def search_destinations(catalog, preferences, service, run_at, progress=None):
    """Filter before fetching; reuse the production save and scoring paths."""
    eligible = [d for d in catalog if is_eligible(d, preferences)]
    if not eligible:
        return {"rows": [], "errors": {}, "cached": 0, "eligible": 0}
    results = service.forecast_many(eligible, on_progress=progress)
    forecasts = forecasts_from_service(results)
    rows = analyse_destinations(eligible, forecasts, preferences, run_at)
    # A cached forecast may have lost its fifth-day coverage as time moved on.
    # Refresh only those cached groups once, using the same service/save path.
    refresh_ids = {
        r["city_id"]
        for r in rows
        if r["reason"] in {"missing_periods", "stale_forecast"}
        and results[r["city_id"]]["from_cache"]
    }
    batch_stopped = any(
        r["error"] and r["error"]["code"] in WeatherService.BATCH_STOP_CODES
        for r in results.values()
    )
    # A coverage retry must obey the same global stop as the first pass.
    if refresh_ids and not batch_stopped:
        refreshed = service.forecast_many(
            [d for d in eligible if d.city_id in refresh_ids],
            force_refresh=True,
            on_progress=progress,
        )
        results.update(refreshed)
        forecasts = forecasts_from_service(results)
        rows = analyse_destinations(eligible, forecasts, preferences, run_at)
    storage_error = next((r["error"] for r in results.values()
                          if r["error"] and r["error"]["code"] == "storage"
                          and not r["error"].get("skipped")), None)
    storage_failure = None
    if storage_error:
        storage_failure = {
            "guidance": storage_error.get("storage_guidance", ""),
            "skipped": sum(
                bool(r["error"] and r["error"].get("skipped"))
                for r in results.values()
            ),
        }
    return {
        "rows": rows,
        "errors": {
            city: result["error"]["code"]
            for city, result in results.items()
            if result["error"]
        },
        "storage_failure": storage_failure,
        "cached": sum(r["from_cache"] for r in results.values()),
        "eligible": len(eligible),
        "forecasts": forecasts,
    }


def render_storage_failure(failure):
    """Show safe file guidance; never display a raw provider/CSV exception."""
    if not failure:
        return
    st.error("Weather loading stopped because local storage failed.")
    st.write(failure.get("guidance") or MESSAGES["storage"])
    skipped = failure.get("skipped", 0)
    if skipped:
        st.caption(
            f"{skipped} remaining destinations were not requested after "
            "the storage failure; they did not each fail separately."
        )
    service = st.session_state.get("weather_service")
    pending = service.unsaved_record_count if service is not None else 0
    if pending:
        st.warning(
            f"{pending} fetched weather records are waiting to be saved "
            "in this session. Keep this tab and app running. After fixing "
            "the file issue, use Search destinations or Refresh weather "
            "overview; saving is retried before any new request."
        )
    else:
        st.info(
            "After fixing the file issue, use Search destinations or "
            "Refresh weather overview to retry."
        )


def forecast_boundary_crossed(rows, run_at, days):
    """Explain missing coverage when a load crosses a required daytime slot.

    Preserve the requested window and never fabricate or drop its slots.
    An explicit new search can evaluate the saved forecasts at a new time.
    """
    slots = expected_period_times(run_at, days)
    return bool(slots) and any(
        row.get("reason") == "missing_periods"
        and row.get("forecast_retrieved_at_utc")
        and datetime.fromisoformat(row["forecast_retrieved_at_utc"])
        >= slots[0]
        for row in rows
    )


def _seed_widgets(preferences, overwrite=False):
    for key, field in WIDGETS.items():
        if overwrite or key not in st.session_state:
            value = getattr(preferences, field)
            if field in {"activities", "destination_sizes"}:
                value = list(value) or ["All"]
            st.session_state[key] = value
        if key in CATEGORY_WIDGETS:
            # Migrate old numeric controls safely before creating widgets.
            st.session_state[key] = category_limit(
                st.session_state[key], CATEGORY_WIDGETS[key]
            )


def _reset(defaults):
    preferences = initial_preferences(utc_now(), defaults)
    st.session_state.search_preferences = preferences
    _seed_widgets(preferences, overwrite=True)


def normalize_all_selection(values):
    """Use the most recently chosen option to make All exclusive."""
    values = list(values or ())
    if not values or values[-1] == "All":
        return ["All"]
    return [value for value in values if value != "All"]


def _keep_all_exclusive(key):
    st.session_state[key] = normalize_all_selection(st.session_state[key])


def _selection(values):
    return () if not values or "All" in values else tuple(values)


def _controls(catalog, defaults):
    _seed_widgets(st.session_state.search_preferences)
    with st.container(border=True, key="trip_form"):
        days, low, high = st.columns(3)
        with days:
            st.selectbox(
                "Forecast window (days from now)", [1, 2, 3, 4, 5],
                key="_trip_days", format_func=lambda n: f"Next {n} days",
            )
        with low:
            st.number_input("Minimum comfortable temperature (°C)",
                            step=1.0, key="_trip_min")
        with high:
            st.number_input("Maximum comfortable temperature (°C)",
                            step=1.0, key="_trip_max")
        rain, wind = st.columns(2)
        with rain:
            st.selectbox(
                "Preferred rain likelihood", list(RAIN_CHOICES),
                format_func=RAIN_CHOICES.__getitem__, key="_trip_rain",
                help="Rewards this probability range, not rainfall intensity.",
            )
        with wind:
            st.selectbox(
                "Preferred wind level", list(WIND_CHOICES),
                format_func=WIND_CHOICES.__getitem__, key="_trip_wind",
                help="Rewards the selected range, including its lower bound.",
            )
        activities, sizes = st.columns(2)
        with activities:
            st.multiselect(
                "Activities",
                ["All"] + sorted({t for d in catalog for t in d.activities}),
                key="_trip_activities", on_change=_keep_all_exclusive,
                args=("_trip_activities",),
                help="Choose activities or All. Clearing means All.",
            )
        with sizes:
            st.multiselect(
                "Destination size",
                ["All"] + sorted({d.destination_size for d in catalog}),
                key="_trip_sizes", on_change=_keep_all_exclusive,
                args=("_trip_sizes",),
                help="Choose sizes or All. Clearing means All.",
            )
        st.button("Reset to seasonal defaults", key="reset_preferences",
                  on_click=_reset, args=(defaults,))
    try:
        preferences = SearchPreferences(
            rain_preference=(
                RAIN_CHOICES[st.session_state._trip_rain].split()[0]),
            wind_preference=(
                WIND_CHOICES[st.session_state._trip_wind].split()[0]),
            days=st.session_state._trip_days,
            temperature_min_c=st.session_state._trip_min,
            temperature_max_c=st.session_state._trip_max,
            max_precipitation_probability_pct=st.session_state._trip_rain,
            max_wind_kmh=st.session_state._trip_wind,
            activities=_selection(st.session_state._trip_activities),
            destination_sizes=_selection(st.session_state._trip_sizes),
        )
    except ValueError:
        if st.session_state._trip_min > st.session_state._trip_max:
            st.error(
                "Minimum temperature cannot be higher than maximum "
                "temperature. Adjust your temperature range."
            )
        else:
            st.error(
                "These preferences could not be validated. Check your "
                "temperature values or reset to seasonal defaults."
            )
        return None
    st.session_state.search_preferences = preferences
    return preferences


def ranking_table(rows, catalog):
    """Presentation only: preserve engine order and label units/reasons."""
    places = {d.city_id: d for d in catalog}
    table = []
    for row in rows:
        d = places[row["city_id"]]
        table.append(
            {
                "City": d.city,
                "Region": d.region,
                "Trip score / 100": row["final_score"],
                "Drive (h:mm)": d.car_duration_min,
                "Distance (km)": d.car_distance_km,
                "Forecast retrieved (UTC)": row["forecast_retrieved_at_utc"],
            }
        )
    durations = duration_column(row["Drive (h:mm)"] for row in table)
    for row, duration in zip(table, durations):
        row["Drive (h:mm)"] = duration
    return table


def _render_results(catalog, current_preferences, defaults):
    if "search_analysis_rows" not in st.session_state:
        st.info("Choose your preferences, then search for a weather match.")
        return
    state = st.session_state
    render_storage_failure(state.get("search_storage_failure"))
    rows = state.search_analysis_rows
    searched = state.search_result_preferences
    if (current_preferences is None
            or asdict(current_preferences) != asdict(searched)):
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
        "(18:00 excluded), checked in three-hour daytime forecast slots."
    )
    rain_label = preferred_label(
        searched.rain_preference, RAIN_CHOICES,
        searched.max_precipitation_probability_pct, "%")
    wind_label = preferred_label(
        searched.wind_preference, WIND_CHOICES, searched.max_wind_kmh, " km/h")
    st.caption(
        f"Preferences: {searched.temperature_min_c:g}–"
        f"{searched.temperature_max_c:g} °C · preferred rain probability: "
        f"{rain_label} · preferred wind: {wind_label}. Activities: "
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
        st.caption(
            f"Oldest forecast was retrieved {duration_text(oldest_age)} h ago."
        )
        if oldest_age > 180:
            st.warning(
                "These saved results are now over three hours old. "
                "Search again before choosing a destination."
            )
    if forecast_boundary_crossed(rows, run_at, searched.days):
        st.warning(
            "This load crossed a daytime forecast-slot boundary. Some "
            "forecasts cannot cover the original window. Search again "
            "to start a new window; suitable saved data will be reused."
        )
    table = ranking_table(rows, catalog)
    places = {d.city_id: d for d in catalog}
    recommendations = available[:defaults["recommendation_count"]]
    high_wind_ids = {r['city_id'] for r in recommendations
                     if r['max_wind_kmh'] >= 39}
    high_wind = len(high_wind_ids)
    if high_wind:
        st.warning(f"{high_wind} of your top recommendations include "
                   "high forecast wind "
                   "(39+ km/h), even if it matches your preference.")
    if available:
        st.html(
            '<div class="wi-recommendation-heading"><div>'
            '<p class="wi-eyebrow">Personalized selection</p>'
            '<h2>Your recommendation</h2></div>'
            '<span class="wi-forecast-badge">OpenWeather forecast · '
            f'next {searched.days} day(s)</span></div>'
        )
        recommendation_cards(recommendations, places, high_wind_ids)
    else:
        st.warning(
            "No complete usable forecasts for this search. "
            "See each destination's reason below."
        )
    with st.expander("Full ranking and forecast details"):
        st.caption(
            "Trip score /100 measures weather against your chosen "
            "preferences, minus the driving-time penalty. "
            "The cards and table show the same score."
        )
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            alt="All eligible destinations ranked by weather and driving time",
            column_config={
                label: st.column_config.NumberColumn(label, format="%.1f")
                for label in [
                    "Trip score / 100",
                ]
            },
        )
        for row in rows:
            if row["status"] != "available":
                reason = state.search_errors.get(row["city_id"], row["reason"])
                message = MESSAGES.get(reason, "Forecast unavailable.")
                st.caption(f"{places[row['city_id']].city}: {message}")
    with st.expander("How the ranking works"):
        st.write(
            "Trip score uses temperature (45%), preferred rain range "
            "(35%) and preferred wind range (20%). Full points inside each "
            "target; gradual penalties outside. The window combines 80% "
            "average and 20% worst-quarter scores. Trip score subtracts "
            "2 points per one-way driving hour, capped at 15. "
            "Scores are preferences, not probabilities or safety advice."
        )


def render_searcher():
    """Render controls first; network work happens only on explicit search."""
    eyebrow("Find your next escape")
    st.header("Trip Searcher")
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
            if error.code in {"authentication", "storage"}:
                # Fixed local setup guidance from config; never the key.
                st.caption(error.message)
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
            state.search_storage_failure = result.get("storage_failure")
            state.search_cached_count = result["cached"]
            for code in sorted(set(result["errors"].values())):
                names = ", ".join(
                    d.city for d in catalog
                    if result["errors"].get(d.city_id) == code)
                message = MESSAGES.get(code, "Weather is unavailable.")
                st.warning(f"{names}: {message}")
        finally:
            progress.empty()
    _render_results(catalog, preferences, defaults)
