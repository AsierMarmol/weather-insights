"""Executive cards and charts. Calculations live in analytics/executive."""

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from weather_app.executive import decision_signal, daily_score_order
from weather_app.presentation import duration_text

MADRID = ZoneInfo("Europe/Madrid")


def _card(label, value, note, city=False):
    kind = 'wi-value wi-city' if city else 'wi-value'
    return (
        f'<article class="wi-card"><div class="wi-label">{escape(label)}'
        f'</div><div class="{kind}">{escape(str(value))}</div>'
        f'<div class="wi-note">{escape(note)}</div></article>'
    )


def render_kpis(summary):
    count = summary['available']
    leaders = summary['leaders']
    leader = leaders[0] if leaders else None
    leader_note = (
        f'{leader["final_score"]:.1f}/100 · '
        f'{leader["car_distance_km"]:g} km from Madrid'
        if leader else 'Load complete forecasts to rank destinations'
    )
    if len(leaders) > 1:
        leader_note += f' · {len(leaders)} tied for first'
    cards = [
        _card('Forecast coverage', f'{count}/{summary["total"]}',
              'Destinations with complete usable forecasts'),
        _card('Average destination score',
              f'{summary["average_score"]:.1f}/100' if count else '—',
              f'Including driving · {count} ranked destinations'),
        _card('Leading destination', leader['destination'] if leader else '—',
              leader_note, city=True),
        _card('Average rain probability',
              f'{summary["average_rain_probability_pct"]:.1f}%'
              if count else '—',
              f'Daytime average · {count}/{summary["total"]} destinations'),
        _card('Average wind speed',
              f'{summary["average_wind_kmh"]:.1f} km/h' if count else '—',
              f'Daytime average · {count}/{summary["total"]} destinations'),
    ]
    st.html('<section class="wi-kpis">' + ''.join(cards) + '</section>')
    st.html(
        '<section class="wi-card wi-signal">'
        '<div class="wi-eyebrow">Executive readout</div>'
        '<h3>Decision signal</h3><div class="wi-muted">'
        + escape(decision_signal(summary)) + '</div></section>'
    )


def scatter_figure(rows):
    figure = go.Figure(go.Scatter(
        x=[r['car_duration_min'] / 60 for r in rows],
        y=[r['final_score'] for r in rows],
        mode='markers', marker={'color': '#235e50', 'size': 9},
        customdata=[[escape(r['destination']),
                     duration_text(r['car_duration_min']),
                     r['car_distance_km'], r['rank']]
                    for r in rows],
        hovertemplate=('%{customdata[0]}<br>Destination score: %{y:.1f}/100'
                       '<br>Drive: %{customdata[1]} h · %{customdata[2]} km'
                       '<br>Destination rank: %{customdata[3]}'
                       '<extra></extra>'),
    ))
    figure.update_layout(
        height=360, margin=dict(l=10, r=10, t=15, b=20),
        xaxis_title='One-way driving time from Madrid (hours)',
        yaxis_title='Destination score / 100', yaxis_range=[0, 100],
        yaxis_fixedrange=True,
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='#183535'), meta='executive',
    )
    figure.update_xaxes(gridcolor='#e4eae2', zeroline=False,
                        rangemode='tozero', minallowed=0)
    figure.update_yaxes(gridcolor='#e4eae2', zeroline=False)
    return figure


def heatmap_table_html(cells, catalog):
    """Accessible table heatmap; colors encode the same fixed 0–100 score."""
    days = sorted({c['day'] for c in cells})
    lookup = {(c['city_id'], c['day']): c for c in cells}
    rows = []
    places = {place.city_id: place for place in catalog}
    for summary in daily_score_order(cells, catalog):
        place = places[summary['city_id']]
        average = summary['average_score']
        value = f'{average:.1f}/100' if average is not None else '—'
        coverage = (f"{summary['available_days']}/"
                    f"{summary['total_days']} days available")
        partial = (f'<br><small>{coverage}</small>' if
                   summary['available_days'] < summary['total_days'] else '')
        columns = [f'<td class="wi-daily-average" title="{coverage}">'
                   f'<strong>{value}</strong>{partial}</td>']
        for day in days:
            cell = lookup.get((place.city_id, day))
            score = cell['score'] if cell else None
            label = f'{place.city} · Day {day}'
            if cell:
                start, end = [datetime.fromisoformat(cell[k]).astimezone(
                    MADRID).strftime('%d %b %H:%M %Z')
                              for k in ('start', 'end')]
                label += f' · {start} → {end}'
            if score is None:
                value, color = '—', '#e6e9e3'
                label += ' · Forecast unavailable'
            else:
                value = f'{score:.1f}/100'
                label += f' · Destination score: {value}'
                fraction = min(100, max(0, score)) / 100
                rgb = [round(a + (b - a) * fraction) for a, b in
                       zip((245, 247, 231), (166, 207, 139))]
                color = '#' + ''.join(f'{channel:02x}' for channel in rgb)
            columns.append(
                f'<td style="background:{color}" '
                f'title="{escape(label, quote=True)}" '
                f'aria-label="{escape(label, quote=True)}">{value}</td>'
            )
        rows.append('<tr><th scope="row">' + escape(place.city)
                    + '</th>' + ''.join(columns) + '</tr>')
    headers = ''.join(f'<th scope="col">Day {d}</th>' for d in days)
    return (
        '<div class="wi-heatmap-scroll" tabindex="0" role="region" '
        'aria-label="Scrollable daily weather scores for all destinations">'
        '<table class="wi-heatmap-table">'
        '<caption>Daily Destination score including driving · '
        'sorted by average daily score, highest first. This daily average '
        'is not the whole-window score. Missing days are '
        'excluded from the average; partial coverage is labeled. '
        'Darker green means higher scores; grey is unavailable.'
        '</caption><thead><tr><th scope="col">Destination</th>'
        '<th scope="col">Daily avg /100</th>'
        + headers + '</tr></thead><tbody>' + ''.join(rows)
        + '</tbody></table></div>'
    )


def render_details(summary, daily, catalog):
    left, right = st.columns(2)
    with left, st.container(border=True, key='top_panel'):
        st.subheader('Top 5 destinations')
        st.caption('Destination score includes the driving penalty '
                   'from Madrid Km0')
        items = []
        for row in summary['top_five']:
            items.append(
                '<div class="wi-ranked"><div><strong>'
                f'{row["rank"]:02d} · {escape(row["destination"])}'
                '</strong><small>'
                f'{row["mean_temperature_c"]:.1f} °C avg · '
                f'{row["max_precipitation_probability_pct"]:.0f}% max rain · '
                f'{row["max_wind_kmh"]:.0f} km/h max wind</small></div>'
                '<div class="wi-score"><strong>'
                f'{row["final_score"]:.1f}/100</strong><small>'
                f'{row["car_distance_km"]:g} km · '
                f'{duration_text(row["car_duration_min"])} h'
                '</small></div></div>'
            )
        st.html(''.join(items))
        st.caption('Equal scores share a rank; city ID orders tied rows.')
    with right, st.container(border=True, key='scatter_panel'):
        st.subheader('Destination score vs driving time')
        st.caption('The same Destination score as the map and rankings, '
                   'including the driving penalty.')
        st.plotly_chart(scatter_figure(summary['rows']), key='drive_scatter',
                        alt='Destination score including driving penalty '
                            'versus driving hours')
    with st.container(border=True, key='bands_panel'):
        st.subheader('Best destinations by driving time')
        st.caption('Top three available destinations in each one-way band. '
                   'Bars show Destination score /100, including driving.')
        bands = []
        for label, rows in summary['bands'].items():
            contents = ''
            for row in rows:
                score = row['final_score']
                contents += (
                    '<div class="wi-bar"><div><strong>'
                    f'{escape(row["destination"])} · {score:.1f}/100'
                    '</strong><br>'
                    f'{row["car_distance_km"]:g} km · '
                    f'{duration_text(row["car_duration_min"])} h</div>'
                    f'<div class="wi-track"><div class="wi-fill" '
                    f'style="width:{score:.4f}%"></div></div></div>'
                )
            bands.append(f'<article class="wi-band"><h4>{label}</h4>'
                         + (contents or '<p>No ranked destinations.</p>')
                         + '</article>')
        st.html('<div class="wi-bands">' + ''.join(bands) + '</div>')
    with st.expander('Destination-by-day weather heatmap'):
        st.caption('Each column is the next successive 24-hour window from '
                   'this overview load, using Madrid daytime slots only. '
                   'Scores include driving and can differ by day. '
                   'Grey cells are unavailable, never zero-score estimates. '
                   'Hover a scored cell for its date/time boundaries.')
        st.html(heatmap_table_html(daily, catalog))
        missing = [c for c in daily if c['score'] is None]
        if missing:
            names = {d.city_id: d.city for d in catalog}
            st.dataframe(pd.DataFrame([{
                'Destination': names[c['city_id']], 'Day': c['day'],
                'Reason': c['reason'], 'Start (UTC)': c['start'],
                'End (UTC)': c['end'],
            } for c in missing]), hide_index=True)
