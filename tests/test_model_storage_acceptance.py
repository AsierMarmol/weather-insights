"""P5.1 model/storage acceptance checks.

The genuine catalog and weather file are only ever read here, never written:
every write goes to a copy under pytest's temporary directory, and each test
asserts the repository files are unchanged. Records appended to those copies
are synthetic test inputs.
"""

import math
import os
import stat
import sys
from collections import defaultdict
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from weather_app import storage
from weather_app.models import (
    RECORD_FIELDS,
    Destination,
    SearchPreferences,
    WeatherRecord,
)
from weather_app.storage import (
    CATALOG_PATH,
    WEATHER_RECORDS_PATH,
    CatalogError,
    StorageError,
    WeatherStore,
    load_destinations,
)

POSIX_ONLY = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX permission bits"
)
# P2.5 saved Toledo, Segovia and Seville; later genuine saves may add more.
P25_CITIES = {"ES-45168", "ES-40194", "ES-41091"}


@pytest.fixture(autouse=True)
def genuine_files_untouched():
    paths = (CATALOG_PATH, WEATHER_RECORDS_PATH)
    before = {path: (path.read_bytes(), path.stat().st_mode) for path in paths}
    yield
    for path in paths:
        assert (path.read_bytes(), path.stat().st_mode) == before[path]


@pytest.fixture
def genuine_copy(tmp_path):
    copy = tmp_path / "weather" / "weather_records.csv"
    copy.parent.mkdir()
    copy.write_bytes(WEATHER_RECORDS_PATH.read_bytes())
    return WeatherStore(copy)


def synthetic_batch(template, periods=2):
    """New synthetic forecast rows shaped like a genuine record."""
    fetch_id = WeatherRecord.new_fetch_id()
    retrieved = template.retrieved_at_utc + timedelta(days=30)
    return [
        replace(
            template,
            fetch_id=fetch_id,
            kind="forecast",
            retrieved_at_utc=retrieved,
            valid_at_utc=retrieved + timedelta(hours=3 * (index + 1)),
            temperature_c=18.0,
            precipitation_probability_pct=10.0,
        )
        for index in range(periods)
    ]


def leftovers(store):
    return sorted(p.name for p in store.path.parent.iterdir())


# --- genuine data continuity (read-only)


def test_genuine_store_reloads_consistently_with_the_catalog():
    catalog = {d.city_id: d for d in load_destinations()}
    records = WeatherStore().load()
    assert len(records) >= 164
    assert len({r.key for r in records}) == len(records)
    assert P25_CITIES <= {r.city_id for r in records} <= set(catalog)

    groups = defaultdict(list)
    for record in records:
        place = catalog[record.city_id]
        # Provider coordinates lie close to the catalog point (< ~11 km).
        assert math.dist(
            (record.latitude, record.longitude),
            (place.latitude, place.longitude),
        ) < 0.1
        groups[record.fetch_id].append(record)
    for group in groups.values():
        identity = {(r.city_id, r.kind, r.retrieved_at_utc) for r in group}
        assert len(identity) == 1
        if group[0].kind == "current":
            assert len(group) == 1


def test_latest_genuine_forecast_is_one_complete_ordered_fetch():
    store = WeatherStore()
    for city_id in P25_CITIES:
        latest = store.latest_forecast(city_id)
        assert len(latest) == 40  # five days of three-hour periods
        assert latest == sorted(latest)
        assert len({r.fetch_id for r in latest}) == 1
        steps = {
            b.valid_at_utc - a.valid_at_utc for a, b in zip(latest, latest[1:])
        }
        assert steps == {timedelta(hours=3)}
        assert all(r.lead_time > timedelta(0) for r in latest)


def test_genuine_rows_reserialize_to_the_saved_text():
    lines = WEATHER_RECORDS_PATH.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(RECORD_FIELDS)
    records = WeatherStore().load()
    assert len(lines) - 1 == len(records)
    for line, record in zip(lines[1:], records):
        row = record.to_csv_row()
        rebuilt = WeatherRecord.from_csv_row(row)
        assert rebuilt == record
        assert line.split(",")[:6] == [row[f] for f in RECORD_FIELDS[:6]]


# --- persistence on a copy of the genuine file


def test_appending_keeps_every_genuine_byte_and_reloads(genuine_copy):
    original_bytes = genuine_copy.path.read_bytes()
    original = genuine_copy.load()
    batch = synthetic_batch(original[0])

    assert genuine_copy.append(batch) == 2
    assert genuine_copy.path.read_bytes().startswith(original_bytes)
    reloaded = WeatherStore(genuine_copy.path).load()
    assert reloaded == original + batch
    assert genuine_copy.latest_forecast(batch[0].city_id) == batch

    after = genuine_copy.path.read_bytes()
    assert genuine_copy.append(batch) == 0  # retry is a no-op
    assert genuine_copy.path.read_bytes() == after
    assert leftovers(genuine_copy) == ["weather_records.csv"]


@POSIX_ONLY
def test_saving_keeps_the_files_permissions(genuine_copy):
    os.chmod(genuine_copy.path, 0o640)
    genuine_copy.append(synthetic_batch(genuine_copy.load()[0]))
    assert stat.S_IMODE(genuine_copy.path.stat().st_mode) == 0o640


@POSIX_ONLY
def test_first_saved_file_follows_the_umask(tmp_path):
    previous = os.umask(0o022)
    try:
        store = WeatherStore(tmp_path / "new" / "weather_records.csv")
        store.append(synthetic_batch(WeatherStore().load()[0]))
    finally:
        os.umask(previous)
    assert stat.S_IMODE(store.path.stat().st_mode) == 0o644


# --- write failures leave the genuine copy intact


@pytest.mark.parametrize("step", ["fsync", "copymode", "replace"])
def test_write_failures_keep_the_previous_file(
    genuine_copy, monkeypatch, step
):
    before = genuine_copy.path.read_bytes()

    def fail(*args, **kwargs):
        raise OSError(28, "No space left on device")

    target = storage.shutil if step == "copymode" else storage.os
    monkeypatch.setattr(target, step, fail)
    with pytest.raises(StorageError, match="No space left"):
        genuine_copy.append(synthetic_batch(genuine_copy.load()[0]))
    monkeypatch.undo()
    assert genuine_copy.path.read_bytes() == before
    assert leftovers(genuine_copy) == ["weather_records.csv"]
    assert genuine_copy.load() == WeatherStore().load()


def test_failed_copy_mid_write_keeps_the_previous_file(
    genuine_copy, monkeypatch
):
    before = genuine_copy.path.read_bytes()

    def partial_copy(source, target):
        target.write(source.read(100))
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(storage.shutil, "copyfileobj", partial_copy)
    with pytest.raises(StorageError, match="Input/output error"):
        genuine_copy.append(synthetic_batch(genuine_copy.load()[0]))
    assert genuine_copy.path.read_bytes() == before
    assert leftovers(genuine_copy) == ["weather_records.csv"]


def test_temp_name_clash_never_removes_the_other_file(
    genuine_copy, monkeypatch
):
    before = genuine_copy.path.read_bytes()
    monkeypatch.setattr(storage.secrets, "token_hex", lambda n: "clash")
    other = genuine_copy.path.parent / ".weather_records.csv.clash.tmp"
    other.write_text("someone else's file")
    with pytest.raises(StorageError):
        genuine_copy.append(synthetic_batch(genuine_copy.load()[0]))
    assert other.read_text() == "someone else's file"
    assert genuine_copy.path.read_bytes() == before


def test_unreadable_store_is_a_storage_error(genuine_copy, monkeypatch):
    def denied(self):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(storage.Path, "read_bytes", denied)
    with pytest.raises(StorageError, match="Permission denied"):
        genuine_copy.load()


# --- catalog loading


def test_catalog_loads_with_windows_line_endings_and_bom(tmp_path):
    text = CATALOG_PATH.read_bytes().removeprefix(b"\xef\xbb\xbf")
    crlf = text.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    path = tmp_path / "catalog.csv"
    path.write_bytes(b"\xef\xbb\xbf" + crlf)
    assert load_destinations(path) == load_destinations()


def test_non_utf8_catalog_is_a_catalog_error(tmp_path):
    path = tmp_path / "catalog.csv"
    path.write_bytes(CATALOG_PATH.read_bytes() + "Cádiz\n".encode("latin-1"))
    with pytest.raises(CatalogError, match="not valid UTF-8"):
        load_destinations(path)


def test_catalog_folder_is_a_catalog_error(tmp_path):
    with pytest.raises(CatalogError, match="Cannot read"):
        load_destinations(tmp_path)


# --- OOP behavior used by the rest of the app


def test_models_are_validated_immutable_values():
    toledo = next(d for d in load_destinations() if d.city_id == "ES-45168")
    record = WeatherStore().latest_forecast("ES-45168")[0]
    for value in (toledo, record):
        with pytest.raises(FrozenInstanceError):
            value.city_id = "ES-00000"
        assert value == replace(value) and hash(value) == hash(replace(value))
    with pytest.raises(ValueError):
        replace(toledo, car_duration_min=-1)
    with pytest.raises(ValueError):
        replace(record, kind="history")
    assert isinstance(toledo, Destination)
    assert toledo.drive_hours == pytest.approx(toledo.car_duration_min / 60)
    assert SearchPreferences(
        days=2,
        temperature_min_c=10,
        temperature_max_c=20,
        max_precipitation_probability_pct=40,
        max_wind_kmh=30,
    ).horizon == timedelta(days=2)
    assert record.lead_time == record.valid_at_utc - record.retrieved_at_utc
    assert str(toledo) == "Toledo (Castilla-La Mancha)"
    assert str(record).startswith("forecast ES-45168 at ")


def test_store_lock_is_private_and_shared_per_file(tmp_path):
    path = tmp_path / "weather_records.csv"
    first, second = WeatherStore(path), WeatherStore(str(path))
    assert first._WeatherStore__lock is second._WeatherStore__lock
    assert first._WeatherStore__lock is not WeatherStore()._WeatherStore__lock
    assert not hasattr(first, "lock") and not hasattr(first, "_lock")
    with pytest.raises(AttributeError):
        first.path = path  # read-only property
    assert repr(first) == f"WeatherStore({str(path.resolve())!r})"
