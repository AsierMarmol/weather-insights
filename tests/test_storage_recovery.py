"""Storage recovery uses synthetic data and temporary files only."""

import sys
from unittest.mock import Mock

import pytest

from test_service import FlakyStore, NOW, saved_rows
from test_storage import forecast
from weather_fakes import TOLEDO, Clock, FakeSession, catalog_handler
from weather_fakes import make_client
from weather_app import storage
from weather_app.models import WeatherRecord
from weather_app.service import WeatherService
from weather_app.storage import StorageError, WeatherStore


def sharing_violation(code=32):
    error = PermissionError(13, "synthetic sensitive detail")
    error.winerror = code
    return error


@pytest.mark.parametrize("code", [5, 32, 33])
def test_transient_windows_lock_retries_without_duplicate_rows(
    tmp_path, monkeypatch, code
):
    store = WeatherStore(tmp_path / "weather.csv")
    first = forecast(WeatherRecord.new_fetch_id())
    second = forecast(WeatherRecord.new_fetch_id())
    store.append(first)
    replace = storage.os.replace
    attempts = []

    def once_locked(source, target):
        attempts.append(1)
        if len(attempts) == 1:
            raise sharing_violation(code)
        replace(source, target)

    monkeypatch.setattr(storage.os, "replace", once_locked)
    assert store.append(second) == len(second)
    assert len(attempts) == 2
    assert store.load() == first + second


def test_persistent_windows_lock_is_bounded_and_preserves_data(
    tmp_path, monkeypatch
):
    store = WeatherStore(tmp_path / "weather.csv")
    store.append(forecast(WeatherRecord.new_fetch_id()))
    original = store.path.read_bytes()
    blocked = Mock(side_effect=sharing_violation())
    monkeypatch.setattr(storage.os, "replace", blocked)
    with pytest.raises(StorageError) as caught:
        store.append(forecast(WeatherRecord.new_fetch_id()))
    assert blocked.call_count == 3
    assert "locked" in caught.value.guidance.lower()
    assert "Windows error 32" in caught.value.guidance
    assert "sensitive" not in caught.value.guidance
    assert store.path.read_bytes() == original
    assert list(store.path.parent.iterdir()) == [store.path]


@pytest.mark.parametrize("errno, wording", [(13, "permission"), (28, "space")])
def test_non_lock_errors_are_not_retried(
    tmp_path, monkeypatch, errno, wording
):
    store = WeatherStore(tmp_path / "weather.csv")
    blocked = Mock(side_effect=OSError(errno, "do not display this"))
    monkeypatch.setattr(storage.os, "replace", blocked)
    with pytest.raises(StorageError) as caught:
        store.append(forecast(WeatherRecord.new_fetch_id()))
    assert blocked.call_count == 1
    assert wording in caught.value.guidance.lower()
    assert "do not display" not in caught.value.guidance
    assert not store.path.exists()


def test_refresh_saves_pending_batch_before_another_http_request(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = FlakyStore(tmp_path / "weather.csv", failures=1)
    service = WeatherService(make_client(session, clock), store, clock=clock)
    failed = service.forecast(TOLEDO)
    assert failed["error"]["code"] == "storage"
    assert service.unsaved_record_count == 40
    recovered = service.forecast(TOLEDO)
    assert recovered["error"] is None and recovered["from_cache"]
    assert len(session.calls) == 1
    assert service.unsaved_record_count == 0
    assert len(saved_rows(store)) == 40


def test_persistent_save_failure_does_not_refetch(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    store = FlakyStore(tmp_path / "weather.csv", failures=3)
    service = WeatherService(make_client(session, clock), store, clock=clock)
    service.forecast(TOLEDO)
    failed = service.forecast(TOLEDO)
    assert failed["error"]["code"] == "storage"
    assert "storage_guidance" in failed["error"]
    assert service.unsaved_record_count == 40
    assert len(session.calls) == 1


def test_corrupt_csv_has_safe_diagnostic_without_http(tmp_path):
    clock = Clock(NOW)
    session = FakeSession(handler=catalog_handler(clock))
    path = tmp_path / "weather.csv"
    path.write_text("private,unexpected,content\n", encoding="utf-8")
    service = WeatherService(
        make_client(session, clock), WeatherStore(path), clock=clock
    )
    result = service.forecast(TOLEDO)
    assert "invalid" in result["error"]["storage_guidance"].lower()
    assert "private" not in result["error"]["storage_guidance"]
    assert not session.calls


@pytest.mark.skipif(sys.platform != "win32", reason="Windows file sharing")
def test_real_windows_open_handle_recovers_after_release(
    tmp_path, monkeypatch
):
    import ctypes
    from ctypes import wintypes

    store = WeatherStore(tmp_path / "weather.csv")
    first = forecast(WeatherRecord.new_fetch_id())
    second = forecast(WeatherRecord.new_fetch_id())
    store.append(first)
    dll = ctypes.WinDLL("kernel32", use_last_error=True)
    dll.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    dll.CreateFileW.restype = wintypes.HANDLE
    dll.CloseHandle.argtypes = [wintypes.HANDLE]
    # Allow reads/writes but deny delete sharing, as a file viewer may do.
    handle = dll.CreateFileW(str(store.path), 0x80000000, 3, None, 3, 0, None)
    assert handle != wintypes.HANDLE(-1).value
    released = []

    def release_after_collision(delay):
        assert not released
        assert store.path.read_bytes().decode("utf-8").count("\n") > 1
        dll.CloseHandle(handle)
        released.append(delay)

    monkeypatch.setattr(storage.time, "sleep", release_after_collision)
    try:
        assert store.append(second) == len(second)
        assert released == [0.1]
        assert store.load() == first + second
    finally:
        if not released:
            dll.CloseHandle(handle)
