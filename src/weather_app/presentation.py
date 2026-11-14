"""Shared presentation; HTML contains no scoring or credential logic."""

import base64
import math
from html import escape
from pathlib import Path

import streamlit as st

from weather_app.config import load_product_defaults, seasonal_defaults

ASSETS = Path(__file__).resolve().parents[2] / "assets"


@st.cache_data
def image_uri(name):
    return 'data:image/jpeg;base64,' + base64.b64encode(
        (ASSETS / name).read_bytes()).decode('ascii')


def apply_design():
    css = (ASSETS / "design.css").read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")


def eyebrow(text):
    st.html(f'<p class="wi-eyebrow">{escape(text)}</p>')


def credits():
    st.html(
        '<footer class="wi-footer">Weather data provided by '
        '<a href="https://openweathermap.org/">OpenWeather</a>.<br>'
        'Destination references: '
        '<a href="https://www.geonames.org/">GeoNames</a>.<br>'
        'Route estimates: <a href="https://project-osrm.org/">OSRM</a> / '
        '<a href="https://www.openstreetmap.org/copyright">'
        'OpenStreetMap contributors</a>.</footer>'
    )


def open_searcher():
    st.session_state.view = "Searcher"


def render_landing(now):
    eyebrow('Weather Insights · mainland Spain')
    try:
        name, season = seasonal_defaults(now, load_product_defaults())
    except ValueError:
        st.error('The seasonal reference could not be loaded.')
        return
    st.html(
        '<section class="wi-hero"><div class="wi-hero-copy">'
        '<div class="wi-eyebrow">Unplanned escapes</div>'
        '<h1>Your next trip starts with the weather.</h1>'
        '<p>Have a few days off but not sure where to go? Start in Madrid, '
        'tune your interests, and find inspiration for your next escape.</p>'
        '<div class="wi-season"><small>Current season in Spain</small>'
        f'{escape(name)} · suggested range '
        f'{season["min"]:g}–{season["max"]:g} °C</div>'
        '<p><small>Explore mainland Spain by car. Seasonal ranges are '
        'suggested comfort preferences, and you can adjust them in the '
        'Trip Searcher.</small></p></div><div class="wi-hero-photo">'
        f'<img src="{image_uri("travel-globe.jpg")}" '
        'alt="A hand holding a globe against a mountain landscape">'
        '</div></section>'
    )
    st.button('Explore destinations →', key='explore', type='primary',
              on_click=open_searcher)
    st.html('<section class="wi-cards">' + ''.join(
        f'<article class="wi-card"><span>{number}</span>'
        f'<h3>{title}</h3><p>{copy}</p></article>'
        for number, title, copy in [
            ('01', 'Choose the weather',
             'Set your comfortable temperature, rain and wind preferences.'),
            ('02', 'Add your interests',
             'Explore coast, nature, heritage, food or urban experiences.'),
            ('03', 'Compare options',
             'See weather matches and reference driving times from Madrid.'),
        ]) + '</section>')


def recommendation_cards(rows, places, high_wind_ids):
    """Compact catalog facts and existing trip scores, in engine order."""
    cards = []
    for rank, row in enumerate(rows, start=1):
        place = places[row['city_id']]
        wind_alert = (
            '<span class="wi-wind-alert" '
            'title="Forecast wind reaches 39 km/h or more '
            'in a daytime slot during this trip window">'
            '<span class="wi-wind-dot" aria-hidden="true"></span>'
            'High wind</span>'
            if row['city_id'] in high_wind_ids else ''
        )
        facts = [
            ('Departure', 'Madrid, Spain'),
            ('Region', place.region),
            ('Activities', ' · '.join(place.activities)),
            ('Size', place.destination_size),
            ('Drive from Madrid', f'{place.car_distance_km:g} km · '
             f'{duration_text(place.car_duration_min)} h'),
            ('Trip score', f"{row['final_score']:.1f}/100"),
        ]
        chips = ''.join(
            '<div class="wi-trip-chip"><dt>' + escape(label) + '</dt>'
            '<dd' + (' class="wi-trip-fit"' if label == 'Trip score' else '')
            + '>' + escape(value) + '</dd></div>'
            for label, value in facts
        )
        cards.append(
            '<article class="wi-trip-card"><div class="wi-trip-heading">'
            f'<span class="wi-trip-number">{rank:02d}</span><div>'
            '<div class="wi-trip-title">'
            f'<h3>{escape(place.city)}</h3>{wind_alert}</div>'
            f'<p>{escape(place.region)} · '
            f'{escape(place.destination_size)}</p></div></div>'
            f'<dl class="wi-trip-facts">{chips}</dl></article>'
        )
    st.html('<section class="wi-trip-list" '
            'aria-label="Ranked trip recommendations">'
            + ''.join(cards) + '</section>')


def duration_text(minutes, width=1):
    """Whole elapsed minutes as hours:minutes, without a 24-hour wrap."""
    if minutes is None or not math.isfinite(minutes):
        return '—'
    hours, remainder = divmod(int(max(0, minutes)), 60)
    return f'{hours:0{width}d}:{remainder:02d}'


def duration_column(values):
    """Pad hours consistently so displayed table durations sort correctly."""
    values = list(values)
    longest = max((int(max(0, v)) // 60 for v in values
                   if v is not None and math.isfinite(v)), default=0)
    width = max(2, len(str(longest)))
    return [None if v is None or not math.isfinite(v)
            else duration_text(v, width) for v in values]
