from pathlib import Path

import streamlit as st

from weather_app.scoring import VERSION

from weather_app.dashboard import render_dashboard_page
from weather_app.presentation import (
    apply_design, credits, render_landing,
)
from weather_app.searcher import render_searcher, utc_now

st.set_page_config(page_title="Weather Insights", layout="wide",
                   initial_sidebar_state="expanded")
previous = st.session_state.get("scoring_version")
old_search = st.session_state.get("search_result_preferences")
old_overview = st.session_state.get("dashboard_overview", {}).get(
    "preferences")
legacy = any(p is not None and not hasattr(p, "scoring_mode")
             for p in (old_search, old_overview))
if (previous is not None and previous != VERSION) or legacy:
    for key in list(st.session_state):
        if key.startswith("search_") or key in {
            "dashboard_overview", "dashboard_error",
            "dashboard_attempted_days"
        }:
            del st.session_state[key]
st.session_state.scoring_version = VERSION

apply_design()
st.sidebar.image(
    str(Path(__file__).resolve().parent / "assets" / "openweather-logo.jpg"),
    width=160, alt="OpenWeather logo",
)
page = st.sidebar.radio(
    "View", ["Landing Page", "Searcher", "Dashboard"], key="view",
    format_func=lambda v: "Trip Searcher" if v == "Searcher" else v,
    label_visibility="collapsed",
)
with st.sidebar.container(key="sidebar_credits"):
    st.caption("A spontaneous trip starts with a good idea.")

if page == "Landing Page":
    render_landing(utc_now())
elif page == "Searcher":
    render_searcher()
else:
    render_dashboard_page()
credits()
