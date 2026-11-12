import streamlit as st

from weather_app.dashboard import render_dashboard_page
from weather_app.searcher import render_searcher

st.set_page_config(page_title="Weather Insights", layout="wide")
st.title("Weather Insights")
page = st.sidebar.radio("View", ["Searcher", "Dashboard"])

if page == "Searcher":
    render_searcher()
else:
    render_dashboard_page()
