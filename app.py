from pathlib import Path

import streamlit as st

from weather_app.dashboard import render_dashboard_page
from weather_app.searcher import render_searcher

st.set_page_config(page_title="Weather Insights", layout="wide")
st.title("Weather Insights")
page = st.sidebar.radio("View", ["Searcher", "Dashboard"])
st.sidebar.image(
    str(Path(__file__).resolve().parent / "assets" / "openweather-logo.jpg"),
    width=160,
    alt="OpenWeather logo",
)
st.sidebar.caption(
    "Weather data provided by [OpenWeather](https://openweathermap.org/)."
)
st.sidebar.caption(
    "Destination references: [GeoNames](https://www.geonames.org/). "
    "Route estimates: OSRM / "
    "[OpenStreetMap contributors](https://www.openstreetmap.org/copyright)."
)

if page == "Searcher":
    render_searcher()
else:
    render_dashboard_page()
