import streamlit as st

st.set_page_config(page_title="Weather Insights", page_icon="\U0001f324️")

st.title("Weather Insights")

page = st.sidebar.radio("View", ["Searcher", "Dashboard"])

if page == "Searcher":
    st.header("Searcher")
    # TODO P4.1: rolling 1-5 days, editable seasonal defaults, All filters, top
    # five + full ranking.

elif page == "Dashboard":
    st.header("Dashboard")
    # TODO P4.2: interactive ranking/weather comparison/all-preferences-period
    # analysis; >=2 real-data charts.
