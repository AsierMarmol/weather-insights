"""P3.2 service tests: real WeatherStore on temporary files, fake HTTP, synthetic weather."""

import csv
from datetime import datetime, timedelta, timezone

import pytest
from weather_fakes import (
    CATALOG,
    DUMMY_KEY,
    LUGO,
    SEGOVIA,
    TOLEDO,
    VITORIA,
    Clock,
    FakeResponse,
    FakeSession,
    catalog_handler,
    current_payload,
    make_client,
)

from weather_app.client import InvalidInputError
from weather_app.service import WeatherService
from weather_app.storage import StorageError, WeatherStore

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 10, 0, tzinfo=UTC)


@pytest.fixture
def setup(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "weather_records.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    return service, session, store, clock


def saved_rows(store):
    if not store.path.exists():
        return []
    with store.path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def assert_result_shape(result):
    assert set(result) == {"records", "from_cache", "error"}


def test_fresh_forecast_is_saved_once_then_served_from_cache(setup):
    service, session, store, clock = setup
    first = service.forecast(TOLEDO)
    assert_result_shape(first)
    assert first["error"] is None and first["from_cache"] is False
    assert len(first["records"]) == 40 and len(saved_rows(store)) == 40
    assert store.latest_forecast(TOLEDO.city_id) == first["records"]

    clock.advance(minutes=20)
    second = service.forecast(TOLEDO)
    assert second["from_cache"] is True and second["records"] == first["records"]
    assert len(session.calls) == 1 and len(saved_rows(store)) == 40


def test_force_refresh_fetches_and_saves_a_new_group(setup):
    service, session, store, _ = setup
    first = service.forecast(TOLEDO)
    second = service.forecast(TOLEDO, force_refresh=True)
    assert second["from_cache"] is False and len(session.calls) == 2
    assert first["records"][0].fetch_id != second["records"][0].fetch_id
    assert len(saved_rows(store)) == 80


def test_forecast_cache_expires_after_three_hours(setup):
    service, session, _, clock = setup
    service.forecast(TOLEDO)
    clock.advance(hours=3)
    assert service.forecast(TOLEDO)["from_cache"] is True  # boundary is still fresh
    clock.advance(seconds=1)
    assert service.forecast(TOLEDO)["from_cache"] is False
    assert len(session.calls) == 2


def test_current_cache_uses_thirty_minutes_and_observation_age(setup):
    service, session, store, clock = setup
    result = service.current(TOLEDO)
    assert result["records"][0].kind == "current" and len(saved_rows(store)) == 1
    clock.advance(minutes=30)
    assert service.current(TOLEDO)["from_cache"] is True
    clock.advance(seconds=1)
    assert service.current(TOLEDO)["from_cache"] is False
    assert len(session.calls) == 2


def test_old_observation_is_not_reused_even_if_recently_retrieved(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(
        handler=lambda url, params: FakeResponse(200, current_payload(TOLEDO, NOW - timedelta(hours=1, minutes=50)))
    )
    service = WeatherService(make_client(session, clock), WeatherStore(tmp_path / "w.csv"), clock=clock)
    service.current(TOLEDO)
    clock.advance(minutes=15)  # retrieval 15 min old, observation 2 h 5 min old
    assert service.current(TOLEDO)["from_cache"] is False


def test_new_service_reuses_fresh_stored_forecast_without_http_or_new_rows(setup):
    service, session, store, clock = setup
    service.forecast(TOLEDO)
    restarted = WeatherService(service.client, WeatherStore(store.path), clock=clock)
    clock.advance(hours=1)
    result = restarted.forecast(TOLEDO)
    assert result["from_cache"] is True and len(result["records"]) == 40
    assert len(session.calls) == 1 and len(saved_rows(store)) == 40


def test_api_failure_saves_and_caches_nothing(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock, failures={TOLEDO.city_id: 404}))
    store = WeatherStore(tmp_path / "w.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    for _ in range(2):
        result = service.forecast(TOLEDO)
        assert result["records"] == [] and result["from_cache"] is False
        assert result["error"]["code"] == "location_not_found"
        assert result["error"]["message"].startswith("Toledo:")
    assert len(session.calls) == 2 and not store.path.exists()


def test_invalid_input_returns_safe_result_without_http(setup):
    service, session, _, _ = setup
    assert service.forecast("Toledo")["error"]["code"] == "invalid_input"
    assert service.current(TOLEDO, force_refresh="yes")["error"]["code"] == "invalid_input"
    assert session.calls == []


class FlakyStore(WeatherStore):
    """Real store whose first ``failures`` writes raise like a full or locked disk."""

    def __init__(self, path, failures):
        super().__init__(path)
        self.failures = failures

    def append(self, records):
        if self.failures:
            self.failures -= 1
            raise StorageError("Could not save weather records to w.csv: No space left on device")
        return super().append(records)


def test_storage_failure_is_reported_and_batch_is_kept_for_retry(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = FlakyStore(tmp_path / "w.csv", failures=1)
    service = WeatherService(make_client(session, clock), store, clock=clock)

    failed = service.forecast(TOLEDO)
    assert failed["records"] == [] and failed["error"]["code"] == "storage"
    assert "not used" in failed["error"]["message"]
    assert service.unsaved_record_count == 40 and not store.path.exists()

    # Not cached: the next request fetches again, and the kept batch is saved first.
    ok = service.forecast(SEGOVIA)
    assert ok["error"] is None and service.unsaved_record_count == 0
    assert {row["city_id"] for row in saved_rows(store)} == {TOLEDO.city_id, SEGOVIA.city_id}
    assert len(saved_rows(store)) == 80


def test_retry_unsaved_reports_remaining_records(tmp_path):
    clock = Clock(NOW)
    store = FlakyStore(tmp_path / "w.csv", failures=2)
    service = WeatherService(make_client(FakeSession(handler=catalog_handler(clock)), clock), store, clock=clock)
    service.current(TOLEDO)
    assert service.retry_unsaved() == 1
    assert service.retry_unsaved() == 0 and len(saved_rows(store)) == 1


def test_unreadable_store_is_a_storage_error_before_any_request(tmp_path):
    path = tmp_path / "w.csv"
    path.write_text("not,the,expected,header\n", encoding="utf-8")
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    service = WeatherService(make_client(session, clock), WeatherStore(path), clock=clock)
    result = service.forecast(TOLEDO)
    assert result["error"]["code"] == "storage" and session.calls == []


def test_missing_metric_is_saved_as_blank_not_zero(tmp_path):
    clock = Clock(NOW)
    base = catalog_handler(clock)

    def handler(url, params):
        response = base(url, params)
        del response._payload["list"][0]["pop"]
        return response

    store = WeatherStore(tmp_path / "w.csv")
    service = WeatherService(make_client(FakeSession(handler=handler), clock), store, clock=clock)
    service.forecast(TOLEDO)
    first = min(saved_rows(store), key=lambda row: row["valid_at_utc"])
    assert first["precipitation_probability_pct"] == ""


def test_forecast_many_skips_ordinary_failures(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock, failures={SEGOVIA.city_id: 404}))
    store = WeatherStore(tmp_path / "w.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    progress = []
    results = service.forecast_many(
        [TOLEDO, SEGOVIA, LUGO, TOLEDO],
        on_progress=lambda done, total, city_id, result: progress.append((done, total, city_id)),
    )
    assert list(results) == [TOLEDO.city_id, SEGOVIA.city_id, LUGO.city_id]
    assert results[SEGOVIA.city_id]["error"]["code"] == "location_not_found"
    assert results[TOLEDO.city_id]["error"] is None and results[LUGO.city_id]["error"] is None
    assert progress == [(1, 3, TOLEDO.city_id), (2, 3, SEGOVIA.city_id), (3, 3, LUGO.city_id)]
    assert {row["city_id"] for row in saved_rows(store)} == {TOLEDO.city_id, LUGO.city_id}
    assert {row["provider_city_id"] for row in saved_rows(store) if row["city_id"] == LUGO.city_id} == {"3117814"}


@pytest.mark.parametrize(("status", "code"), [(401, "authentication"), (429, "rate_limited")])
def test_forecast_many_stops_on_key_or_quota_failure(tmp_path, status, code):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock, failures={SEGOVIA.city_id: status}))
    service = WeatherService(make_client(session, clock), WeatherStore(tmp_path / "w.csv"), clock=clock)
    results = service.forecast_many([TOLEDO, SEGOVIA, LUGO, VITORIA])
    assert len(session.calls) == 2  # Lugo and Vitoria are never requested
    assert results[TOLEDO.city_id]["error"] is None
    for city_id in (SEGOVIA.city_id, LUGO.city_id, VITORIA.city_id):
        assert results[city_id]["error"]["code"] == code and results[city_id]["records"] == []
    assert "not requested" in results[LUGO.city_id]["error"]["message"]


def test_forecast_many_reuses_cache_and_rejects_bad_input(setup):
    service, session, _, _ = setup
    service.forecast_many([TOLEDO, SEGOVIA])
    again = service.forecast_many([TOLEDO, SEGOVIA])
    assert all(result["from_cache"] for result in again.values())
    assert len(session.calls) == 2
    for bad in ("Toledo", [TOLEDO, "Segovia"], None):
        with pytest.raises(InvalidInputError):
            service.forecast_many(bad)


def test_whole_catalog_batch_saves_every_city_once(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = WeatherStore(tmp_path / "w.csv")
    service = WeatherService(make_client(session, clock), store, clock=clock)
    results = service.forecast_many(list(CATALOG.values()))
    assert len(results) == 83 and all(r["error"] is None for r in results.values())
    assert len(session.calls) == 83 and len(saved_rows(store)) == 83 * 40


def test_results_and_repr_never_contain_the_key(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock, failures={TOLEDO.city_id: 401}))
    service = WeatherService(make_client(session, clock), WeatherStore(tmp_path / "w.csv"), clock=clock)
    result = service.forecast(TOLEDO)
    assert DUMMY_KEY not in repr(result) and DUMMY_KEY not in repr(service)
