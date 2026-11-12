"""P3.1 catalog and storage tests.

Weather records here are synthetic and only ever written under pytest's
temporary directories; the genuine data/weather folder is never touched.
"""

import threading
from datetime import datetime, timedelta, timezone

import pytest

from weather_app import storage
from weather_app.models import ACTIVITIES, DESTINATION_SIZES, RECORD_FIELDS, WeatherRecord
from weather_app.storage import (
    CATALOG_FIELDS,
    CatalogError,
    StorageError,
    WeatherStore,
    load_destinations,
)

UTC = timezone.utc
RUN = datetime(2026, 11, 11, 18, 30, tzinfo=UTC)
HEADER = ",".join(RECORD_FIELDS) + "\n"


def forecast(fetch_id, city_id="ES-45168", retrieved=RUN, periods=3, **metrics):
    first = datetime(2026, 11, 12, 9, tzinfo=UTC)
    values = dict(temperature_c=20.0, wind_kmh=10.0, precipitation_probability_pct=20.0)
    values.update(metrics)
    return [
        WeatherRecord(
            fetch_id=fetch_id,
            city_id=city_id,
            kind="forecast",
            retrieved_at_utc=retrieved,
            valid_at_utc=first + timedelta(hours=3 * index),
            latitude=39.8581,
            longitude=-4.0226,
            humidity_pct=None,
            cloud_pct=75.0,
            provider_city_id=2510409,
            provider_city_name="Toledo",
            **values,
        )
        for index in range(periods)
    ]


def current(fetch_id, city_id="ES-40194"):
    return WeatherRecord(
        fetch_id=fetch_id,
        city_id=city_id,
        kind="current",
        retrieved_at_utc=RUN,
        valid_at_utc=RUN - timedelta(minutes=12),
        latitude=40.9481,
        longitude=-4.1184,
        temperature_c=9.5,
        wind_kmh=None,
        provider_city_id=3109256,
        provider_city_name="Segovia",
    )


@pytest.fixture
def store(tmp_path):
    return WeatherStore(tmp_path / "weather" / "weather_records.csv")


# --- catalog ------------------------------------------------------------------


def test_real_catalog_loads_all_83_destinations():
    destinations = load_destinations()
    assert len(destinations) == 83
    assert len({d.city_id for d in destinations}) == 83
    sizes = [d.destination_size for d in destinations]
    assert {size: sizes.count(size) for size in DESTINATION_SIZES} == {
        "Large city": 14, "Medium city": 26, "Small city or town": 43,
    }
    assert {tag for d in destinations for tag in d.activities} == set(ACTIVITIES)
    lugo = next(d for d in destinations if d.city_id == "ES-27028")
    assert (lugo.city, lugo.latitude, lugo.longitude) == ("Lugo", 43.0, -7.5667)
    assert (lugo.car_distance_km, lugo.car_duration_min) == (498.0, 329.0)
    barcelona = destinations[0]
    assert barcelona.activities == ("Coast", "History and heritage", "Urban experiences")


def test_default_paths_are_inside_the_repository():
    assert storage.CATALOG_PATH.is_absolute() and storage.CATALOG_PATH.exists()
    assert storage.WEATHER_RECORDS_PATH.parent == storage.PROJECT_ROOT / "data" / "weather"
    assert WeatherStore().path == storage.WEATHER_RECORDS_PATH


def write_catalog(tmp_path, *rows, header=",".join(CATALOG_FIELDS)):
    path = tmp_path / "catalog.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


TOLEDO_ROW = (
    'ES-45168,Toledo,Castilla-La Mancha,72,61,39.8581,-4.02263,'
    '"History and heritage;Food and gastronomy",Small city or town'
)


def test_catalog_loader_parses_semicolon_activities(tmp_path):
    [toledo] = load_destinations(write_catalog(tmp_path, TOLEDO_ROW))
    assert toledo.activities == ("History and heritage", "Food and gastronomy")
    assert toledo.drive_hours == pytest.approx(61 / 60)


@pytest.mark.parametrize(
    "rows, header, message",
    [
        ((TOLEDO_ROW, TOLEDO_ROW), None, "duplicate city_id"),
        ((TOLEDO_ROW.replace(",72,", ",far,"),), None, "car_distance_km"),
        ((TOLEDO_ROW.replace("Small city or town", "Village"),), None, "line 2"),
        ((TOLEDO_ROW + ",extra",), None, "wrong number of fields"),
        ((TOLEDO_ROW,), "city_id,city,region", "columns"),
        ((), None, "no destinations"),
    ],
)
def test_catalog_loader_reports_bad_rows(tmp_path, rows, header, message):
    kwargs = {} if header is None else {"header": header}
    with pytest.raises(CatalogError, match=message):
        load_destinations(write_catalog(tmp_path, *rows, **kwargs))


def test_missing_catalog_is_a_catalog_error(tmp_path):
    with pytest.raises(CatalogError, match="Cannot read"):
        load_destinations(tmp_path / "absent.csv")


# --- WeatherStore: saving and reloading ----------------------------------------


def test_missing_store_loads_empty_and_is_not_created(store):
    assert store.load() == []
    assert store.latest_forecast("ES-45168") == []
    assert store.append([]) == 0
    assert not store.path.exists()


def test_append_creates_file_with_exact_header_and_round_trips(store):
    records = forecast(WeatherRecord.new_fetch_id()) + [current(WeatherRecord.new_fetch_id())]
    assert store.append(records) == 4
    text = store.path.read_text(encoding="utf-8")
    assert text.startswith(HEADER)
    assert "\r" not in text
    assert store.load() == records
    # Missing values are blank cells, not zeros.
    segovia_line = text.splitlines()[-1].split(",")
    assert segovia_line[RECORD_FIELDS.index("wind_kmh")] == ""
    assert segovia_line[RECORD_FIELDS.index("precipitation_probability_pct")] == ""


def test_load_filters_by_city_and_kind(store):
    toledo = forecast(WeatherRecord.new_fetch_id())
    segovia = current(WeatherRecord.new_fetch_id())
    store.append(toledo + [segovia])
    assert store.load(city_id="ES-40194") == [segovia]
    assert store.load(kind="forecast") == toledo
    assert store.load(city_id="ES-40194", kind="forecast") == []
    with pytest.raises(ValueError):
        store.load(kind="history")


def test_retrying_a_save_is_idempotent(store):
    records = forecast(WeatherRecord.new_fetch_id())
    assert store.append(records) == 3
    before = store.path.read_bytes()
    assert store.append(records) == 0
    assert store.append(records[:1]) == 0
    assert store.path.read_bytes() == before


def test_distinct_fetch_with_same_provider_times_is_kept(store):
    store.append(forecast(WeatherRecord.new_fetch_id()))
    store.append(forecast(WeatherRecord.new_fetch_id()))
    assert len(store.load()) == 6


def test_conflicting_values_for_a_saved_key_are_rejected(store):
    fetch_id = WeatherRecord.new_fetch_id()
    store.append(forecast(fetch_id))
    before = store.path.read_bytes()
    with pytest.raises(ValueError, match="different values"):
        store.append(forecast(fetch_id, temperature_c=30.0))
    with pytest.raises(ValueError, match="conflicting"):
        store.append(forecast(fetch_id, periods=1) + forecast(fetch_id, periods=1, wind_kmh=1.0))
    assert store.path.read_bytes() == before


def test_append_rejects_non_records(store):
    with pytest.raises(ValueError):
        store.append([{"city_id": "ES-45168"}])


def test_existing_genuine_rows_are_preserved_byte_for_byte(store):
    store.append(forecast(WeatherRecord.new_fetch_id()))
    original = store.path.read_bytes()
    store.append([current(WeatherRecord.new_fetch_id())])
    assert store.path.read_bytes().startswith(original)


def test_instances_share_one_file(store):
    other = WeatherStore(store.path)
    store.append([current(WeatherRecord.new_fetch_id())])
    assert len(other.load()) == 1
    assert repr(other) == f"WeatherStore({str(store.path)!r})"


# --- latest forecast ------------------------------------------------------------


def test_latest_forecast_returns_only_the_newest_group_in_time_order(store):
    older = forecast(WeatherRecord.new_fetch_id(), retrieved=RUN - timedelta(hours=2), periods=4)
    newer = forecast(WeatherRecord.new_fetch_id(), retrieved=RUN, periods=2)
    other_city = forecast(
        WeatherRecord.new_fetch_id(), city_id="ES-41091", retrieved=RUN + timedelta(hours=1)
    )
    store.append(list(reversed(newer)))
    store.append(older)  # saved later, but retrieved earlier
    store.append(other_city)
    latest = store.latest_forecast("ES-45168")
    assert latest == newer  # not stitched with the older group's extra periods
    assert {r.fetch_id for r in latest} == {newer[0].fetch_id}


def test_latest_forecast_ignores_current_observations(store):
    store.append([current(WeatherRecord.new_fetch_id(), city_id="ES-45168")])
    assert store.latest_forecast("ES-45168") == []


# --- failure handling -------------------------------------------------------------


def test_failed_replace_keeps_previous_file_and_cleans_temp(store, monkeypatch):
    store.append(forecast(WeatherRecord.new_fetch_id()))
    before = store.path.read_bytes()

    def broken_replace(*args):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(storage.os, "replace", broken_replace)
    with pytest.raises(StorageError, match="Could not save"):
        store.append([current(WeatherRecord.new_fetch_id())])
    assert store.path.read_bytes() == before
    assert sorted(p.name for p in store.path.parent.iterdir()) == [store.path.name]


def test_unwritable_location_is_a_storage_error(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    store = WeatherStore(blocker / "weather_records.csv")
    with pytest.raises(StorageError):
        store.append([current(WeatherRecord.new_fetch_id())])


@pytest.mark.parametrize(
    "content, message",
    [
        ("wrong,header\n", "expected header"),
        ("", "expected header"),
        (HEADER + "1,abc", "incomplete row"),
        (HEADER + "1,not-a-uuid,ES-45168,forecast,,,,,,,,,,1,X\n", "line 2"),
    ],
)
def test_damaged_files_raise_and_are_never_appended_to(store, content, message):
    store.path.parent.mkdir(parents=True)
    store.path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError, match=message):
        store.load()
    with pytest.raises(StorageError):
        store.append([current(WeatherRecord.new_fetch_id())])
    assert store.path.read_text(encoding="utf-8") == content


def test_concurrent_appends_in_one_process_are_serialized(store):
    batches = [forecast(WeatherRecord.new_fetch_id()) for _ in range(8)]
    threads = [threading.Thread(target=WeatherStore(store.path).append, args=(b,)) for b in batches]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(store.load()) == 24
    assert len({r.fetch_id for r in store.load()}) == 8



# --- schema version regression ----------------------------------------------------


def test_integer_schema_version_saves_and_reloads(store):
    records = forecast(WeatherRecord.new_fetch_id())
    assert all(type(r.schema_version) is int for r in records)
    store.append(records)
    lines = store.path.read_text(encoding="utf-8").splitlines()[1:]
    assert all(line.startswith("1,") for line in lines)
    assert store.load() == records


@pytest.mark.parametrize("version", [1.0, True, "1", 2])
def test_rejected_schema_versions_never_reach_an_existing_store(store, version):
    store.append(forecast(WeatherRecord.new_fetch_id()))
    before = store.path.read_bytes()
    with pytest.raises(ValueError, match="schema_version"):
        WeatherRecord(**{**current(WeatherRecord.new_fetch_id()).__dict__, "schema_version": version})
    with pytest.raises(ValueError):
        store.append([{"schema_version": version}])
    assert store.path.read_bytes() == before
    assert len(store.load()) == 3


def test_saved_row_with_float_schema_version_is_reported(store):
    row = current(WeatherRecord.new_fetch_id()).to_csv_row()
    row["schema_version"] = "1.0"
    store.path.parent.mkdir(parents=True)
    store.path.write_text(HEADER + ",".join(row[f] for f in RECORD_FIELDS) + "\n", encoding="utf-8")
    with pytest.raises(StorageError, match="line 2"):
        store.load()


# --- duplicate keys already in a saved file -----------------------------------------


def write_rows(store, *records):
    """Write records straight to the file, bypassing append() (simulates a bad merge/edit)."""
    store.path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(r.to_csv_row()[f] for f in RECORD_FIELDS) for r in records]
    store.path.write_text(HEADER + "\n".join(lines) + "\n", encoding="utf-8")
    return store.path.read_bytes()


def conflicting_pair():
    [original] = forecast(WeatherRecord.new_fetch_id(), periods=1, temperature_c=20.0)
    [changed] = forecast(original.fetch_id, periods=1, temperature_c=27.5)
    assert original.key == changed.key and original != changed
    return original, changed


def test_saved_rows_with_same_key_and_different_values_are_rejected(store):
    original, changed = conflicting_pair()
    write_rows(store, original, current(WeatherRecord.new_fetch_id()), changed)
    with pytest.raises(StorageError, match=r"line 4: conflicting values for the record on line 2"):
        store.load()
    with pytest.raises(StorageError, match="conflicting"):
        store.load(city_id="ES-40194")  # filters cannot hide the inconsistency
    with pytest.raises(StorageError, match="conflicting"):
        store.latest_forecast("ES-45168")


def test_appending_to_a_conflicting_file_fails_without_changing_it(store):
    original, changed = conflicting_pair()
    before = write_rows(store, original, changed)
    for batch in ([current(WeatherRecord.new_fetch_id())], [original], [changed]):
        with pytest.raises(StorageError, match="conflicting"):
            store.append(batch)
        assert store.path.read_bytes() == before
    assert sorted(p.name for p in store.path.parent.iterdir()) == [store.path.name]


def test_identical_duplicate_rows_are_returned_once_and_left_in_place(store):
    records = forecast(WeatherRecord.new_fetch_id(), periods=2)
    before = write_rows(store, records[0], records[1], records[0])
    assert store.load() == records
    assert store.latest_forecast("ES-45168") == records
    # Retrying the save is still idempotent and does not "repair" the file.
    assert store.append(records) == 0
    assert store.path.read_bytes() == before
    # New genuine records are appended after the untouched existing bytes.
    extra = current(WeatherRecord.new_fetch_id())
    assert store.append([extra]) == 1
    assert store.path.read_bytes().startswith(before)
    assert store.load() == records + [extra]


def test_retries_stay_idempotent_and_distinct_fetches_stay_separate_after_fix(store):
    first = forecast(WeatherRecord.new_fetch_id())
    second = forecast(WeatherRecord.new_fetch_id())  # same provider times, new fetch
    assert store.append(first) == 3
    assert store.append(first) == 0
    assert store.append(second) == 3
    assert store.append(first + second) == 0
    saved = store.load()
    assert len(saved) == 6
    assert {r.fetch_id for r in saved} == {first[0].fetch_id, second[0].fetch_id}
    assert store.latest_forecast("ES-45168") == second
