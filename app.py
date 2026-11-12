import streamlit as st

from weather_app.searcher import render_searcher

st.set_page_config(page_title="Weather Insights", layout="wide")
st.title("Weather Insights")
page = st.sidebar.radio("View", ["Searcher", "Dashboard"])

if page == "Searcher":
    render_searcher()
else:
    st.header("Dashboard")
    st.info(
        "The interactive Dashboard is planned for P4.2. "
        "Use Searcher to find and compare destinations now."
    )
