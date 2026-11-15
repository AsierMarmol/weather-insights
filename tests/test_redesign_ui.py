"""New UI journeys; live HTTP blocked, genuine files kept unchanged."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest
from test_dashboard import page  # noqa: F401 -- shared offline fixture

from weather_app import searcher
from weather_app.executive_view import scatter_figure, heatmap_table_html
from weather_fakes import TOLEDO

ROOT = Path(__file__).resolve().parents[1]


def html_text(app):
    return ' '.join(element.proto.body for element in app.get('html'))


def test_landing_uses_real_defaults_and_navigates_without_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError('Landing and navigation must not fetch weather')
    monkeypatch.setattr(requests.Session, 'request', blocked)
    monkeypatch.setattr(searcher, 'utc_now', lambda: datetime(
        2026, 11, 13, 12, tzinfo=timezone.utc))
    data = (ROOT / 'data/weather/weather_records.csv').read_bytes()
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    assert not app.exception
    assert app.sidebar.radio[0].value == 'Landing Page'
    html = html_text(app)
    assert 'Autumn · suggested range 16–24 °C' in html
    assert '14–26' not in html
    assert 'data:image/jpeg;base64,' in html
    app.button(key='explore').click().run()
    assert not app.exception
    assert app.sidebar.radio[0].value == 'Searcher'
    assert app.number_input(key='_trip_min').value == 16
    assert app.selectbox(key='_trip_days').value == 3
    assert (ROOT / 'data/weather/weather_records.csv').read_bytes() == data


def test_executive_charts_share_snapshot_and_navigation_does_not_fetch(
    page,  # noqa: F811 -- injected shared fixture
):
    app, service, session, _, _ = page
    app.button(key='dashboard_load').click().run()
    assert not app.exception
    snapshot = app.session_state['dashboard_overview']
    assert len(snapshot['daily']) == 83 * 3
    assert not app.multiselect
    specs = [json.loads(c.proto.spec) for c in app.get('plotly_chart')]
    scatter = next(s for s in specs if s['data'][0]['type'] == 'scatter')
    expected = sorted(
        [r['final_score'] for r in snapshot['rows']
         if r['status'] == 'available'])
    assert sorted(scatter['data'][0]['y']) == pytest.approx(expected)
    heat = next(e.proto.body for e in app.get('html')
                if 'class="wi-heatmap-table"' in e.proto.body)
    assert heat.count('scope="row"') == 83
    assert heat.count('<td ') == 83 * 4
    assert '<th scope="col">Daily avg /100</th>' in heat
    for day in range(1, 4):
        assert f'<th scope="col">Day {day}</th>' in heat
    html = html_text(app)
    assert '83/83' in html and 'Including driving · 83 ranked' in html
    saved = service.store.path.read_bytes()
    app.sidebar.radio[0].set_value('Landing Page').run()
    app.sidebar.radio[0].set_value('Dashboard').run()
    assert app.session_state['dashboard_overview'] == snapshot
    assert len(session.calls) == 83
    assert service.store.path.read_bytes() == saved


def test_scatter_preserves_units_and_heatmap_keeps_missing_cells():
    figure = scatter_figure([dict(
        car_duration_min=150, weather_match_pct=80, final_score=75,
        destination='Toledo', car_distance_km=74, rank=1,
    )])
    assert list(figure.to_plotly_json()["data"][0]["x"]) == [2.5]
    assert list(figure.to_plotly_json()["data"][0]["y"]) == [75]
    assert list(figure.layout.yaxis.range) == [0, 100]
    assert figure.layout.yaxis.fixedrange is True
    heat = heatmap_table_html([dict(
        city_id=TOLEDO.city_id, day=1, score=None, reason='missing_periods',
        start='2026-11-13T12:00:00Z', end='2026-11-14T12:00:00Z',
        evaluated_periods=0, expected_periods=3,
    )], [TOLEDO])
    assert 'background:#e6e9e3' in heat
    assert 'Forecast unavailable' in heat
    assert '>—</td>' in heat
    assert '>0.0/100</td>' not in heat


def test_first_dashboard_visit_loads_once_and_window_reuses_saved_data(
    page,  # noqa: F811 -- shared fixture
):
    app, service, session, _, factory = page
    del app.session_state['dashboard_attempted_days']
    app.run()  # first entry, no button click
    assert not app.exception
    assert len(session.calls) == 83 and factory.call_count == 1
    assert app.session_state['dashboard_overview']['preferences'].days == 3
    saved = service.store.path.read_bytes()
    app.run()
    app.sidebar.radio[0].set_value('Landing Page').run()
    app.sidebar.radio[0].set_value('Dashboard').run()
    assert len(session.calls) == 83
    app.selectbox(key='dashboard_days').set_value(5).run()
    assert app.session_state['dashboard_overview']['preferences'].days == 5
    assert len(app.session_state['dashboard_overview']['daily']) == 415
    assert len(session.calls) == 83  # shared fresh batches, no second fetch
    assert service.store.path.read_bytes() == saved


def test_auto_load_failure_requires_window_change_or_manual_retry(
    page,  # noqa: F811 -- shared fixture
):
    from weather_app.client import AuthenticationError
    app, service, session, _, factory = page
    factory.side_effect = AuthenticationError('Configure your local key.')
    del app.session_state['dashboard_attempted_days']
    app.run()
    assert not app.exception and app.error
    assert factory.call_count == 1 and not session.calls
    app.run()
    app.sidebar.radio[0].set_value('Landing Page').run()
    app.sidebar.radio[0].set_value('Dashboard').run()
    assert factory.call_count == 1  # no failure loop
    factory.side_effect = None
    app.button(key='dashboard_load').click().run()
    assert not app.exception
    assert len(session.calls) == 83
    assert app.session_state['dashboard_overview']['preferences'].days == 3


def test_failed_window_change_preserves_last_successful_snapshot(
    page,  # noqa: F811 -- shared fixture
):
    from unittest.mock import Mock
    from weather_app.client import AuthenticationError
    app, service, _, _, _ = page
    app.button(key='dashboard_load').click().run()
    original = app.session_state['dashboard_overview']
    service.forecast_many = Mock(side_effect=AuthenticationError('Rejected'))
    app.selectbox(key='dashboard_days').set_value(5).run()
    assert not app.exception and app.error
    assert app.session_state['dashboard_overview'] == original
    assert any('not been refreshed' in element.value for element in app.info)
    app.run()
    assert service.forecast_many.call_count == 1


def test_duration_display_keeps_hours_minutes_and_sort_order():
    from weather_app.presentation import duration_text, duration_column
    assert [duration_text(v) for v in (0, 61, 86, 270, 409, 1501)] == [
        '0:00', '1:01', '1:26', '4:30', '6:49', '25:01']
    assert duration_text(None) == '—'
    assert duration_column([601, 61, None, 270]) == [
        '10:01', '01:01', None, '04:30']
    durations = duration_column([601, 61, 270])
    assert all(value is not None for value in durations)
    assert sorted(value for value in durations if value is not None) == [
        '01:01', '04:30', '10:01']
    assert duration_column([6001, 601]) == ['100:01', '010:01']


def test_equivalent_preferences_after_reload_do_not_warn(
    page,  # noqa: F811 -- shared fixture
):
    from dataclasses import asdict, dataclass, replace
    from weather_app.models import SearchPreferences

    # A reloaded dataclass can have the same values but a different identity.
    @dataclass(frozen=True, kw_only=True)
    class ReloadedPreferences(SearchPreferences):
        pass

    app, _, _, _, _ = page
    app.button(key='dashboard_load').click().run()
    overview = app.session_state['dashboard_overview']
    original = overview['preferences']
    equivalent = ReloadedPreferences(**asdict(original))
    assert original != equivalent  # Reproduces the old comparison problem.
    overview['preferences'] = equivalent
    app.run()
    assert not app.exception
    assert not any('settings have changed' in e.value for e in app.info)
    # A real value change must still identify the older result snapshot.
    overview['preferences'] = replace(equivalent, days=1)
    app.run()
    assert any('settings have changed' in e.value for e in app.info)
