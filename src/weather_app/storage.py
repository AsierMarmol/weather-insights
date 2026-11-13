"""P3.1 catalog loading and weather-record persistence.

``load_destinations`` reads the nine-column destination catalog.
``WeatherStore`` appends normalized weather records to one CSV file and
reads them back. The API service (P3.2) calls ``append`` once for every
fresh successful response; cached redisplays never call it. Paths default
to the repository's data folder, independent of the shell's working
directory.

Write strategy: the existing file is copied byte-for-byte to a temporary
file in the same folder, new rows are appended there, the copy is flushed
to disk and then atomically swapped in with ``os.replace``. The new file
keeps the previous file's permissions (a first file gets the user's normal
umask). A failure at any point leaves the previous file untouched, so
genuine records are never truncated.
"""

from __future__ import annotations

import csv
import errno
import io
import os
import secrets
import shutil
import threading
import time
from collections.abc import Sequence
from pathlib import Path

from weather_app.models import (
    RECORD_FIELDS,
    WEATHER_KINDS,
    Destination,
    WeatherRecord,
    format_utc,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "data" / "reference" / "destinations.csv"
WEATHER_RECORDS_PATH = (
    PROJECT_ROOT / "data" / "weather" / "weather_records.csv"
)

CATALOG_FIELDS = (
    "city_id",
    "city",
    "region",
    "car_distance_km",
    "car_duration_min",
    "latitude",
    "longitude",
    "activities",
    "destination_size",
)


class CatalogError(ValueError):
    """The destination catalog is missing, malformed or inconsistent."""


class StorageError(RuntimeError):
    """Storage failure with safe UI guidance, never raw file contents."""

    def __init__(self, message, *, os_error=None, invalid_file=False):
        super().__init__(message)
        winerror = getattr(os_error, "winerror", None)
        number = getattr(os_error, "errno", None)
        if winerror in {32, 33}:
            guidance = (
                "The weather file is locked by another program. Close "
                "any spreadsheet using it, then retry in this session."
            )
        elif number in {errno.EACCES, errno.EPERM} or winerror == 5:
            guidance = (
                "Permission was denied. Check write access to "
                "data/weather and close programs holding the CSV open."
            )
        elif number == errno.ENOSPC or winerror == 112:
            guidance = "The disk has no space left. Free space, then retry."
        elif invalid_file:
            guidance = (
                "The weather CSV is invalid or incomplete. Preserve a "
                "copy and repair it before retrying; do not delete history."
            )
        else:
            guidance = (
                "The weather file could not be read or saved. Check "
                "data/weather/weather_records.csv and its folder access."
            )
        if type(winerror) is int:
            guidance += f" (Windows error {winerror}.)"
        elif type(number) is int:
            guidance += f" (OS error {number}.)"
        self.guidance = guidance


def _retry_file_lock(action, *args):
    """Bound Windows access/lock retries; never replace a file in place."""
    for attempt in range(3):
        try:
            return action(*args)
        except OSError as error:
            if getattr(error, "winerror", None) not in {5, 32, 33}:
                raise
            if attempt == 2:
                raise
            time.sleep(0.1 * (attempt + 1))


def load_destinations(path: Path = CATALOG_PATH) -> list[Destination]:
    """Load and validate every catalog row, preserving file order."""
    path = Path(path)
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != CATALOG_FIELDS:
                raise CatalogError(
                    f"{path.name} must have exactly these columns:"
                    f" {', '.join(CATALOG_FIELDS)}"
                )
            destinations: list[Destination] = []
            seen: set[str] = set()
            for row in reader:
                line = reader.line_num
                try:
                    destination = _destination_from_row(row)
                except ValueError as error:
                    raise CatalogError(
                        f"{path.name} line {line}: {error}"
                    ) from None
                if destination.city_id in seen:
                    raise CatalogError(
                        f"{path.name} line {line}: duplicate city_id"
                        f" {destination.city_id}"
                    )
                seen.add(destination.city_id)
                destinations.append(destination)
    except OSError as error:
        raise CatalogError(
            f"Cannot read catalog {path.name}: {error.strerror}"
        ) from None
    except UnicodeDecodeError:
        raise CatalogError(f"{path.name} is not valid UTF-8") from None
    if not destinations:
        raise CatalogError(f"{path.name} contains no destinations")
    return destinations


def _destination_from_row(row: dict[str, str | None]) -> Destination:
    if None in row or any(row[name] is None for name in CATALOG_FIELDS):
        raise ValueError("wrong number of fields")
    numbers = {}
    for name in (
        "car_distance_km",
        "car_duration_min",
        "latitude",
        "longitude",
    ):
        try:
            numbers[name] = float(row[name])
        except ValueError:
            raise ValueError(f"{name} is not a number") from None
    activities = tuple(
        tag.strip() for tag in row["activities"].split(";") if tag.strip()
    )
    return Destination(
        city_id=row["city_id"],
        city=row["city"],
        region=row["region"],
        activities=activities,
        destination_size=row["destination_size"],
        **numbers,
    )


class WeatherStore:
    """CSV store for normalized weather records (P2.4 schema version 1)."""

    # One lock per resolved file, shared by every store instance in this
    # process (Streamlit reruns create new instances). Name-mangled so neither
    # callers nor subclasses can replace it and silently lose serialization.
    __locks: dict[Path, threading.Lock] = {}
    __locks_guard = threading.Lock()

    def __init__(self, path: Path = WEATHER_RECORDS_PATH) -> None:
        self._path = Path(path).resolve()
        self.__validated_raw: bytes | None = None
        self.__validated_records: tuple[WeatherRecord, ...] = ()
        with WeatherStore.__locks_guard:
            self.__lock = WeatherStore.__locks.setdefault(
                self._path, threading.Lock()
            )

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:
        return f"WeatherStore({str(self._path)!r})"

    # -- writing

    def append(self, records: Sequence[WeatherRecord]) -> int:
        """Save a fetched batch and return how many new rows were written.

        Saving the same records again (a retry) writes nothing. A record
        whose
        key already exists with different values is a conflict and raises
        ``ValueError``; file problems, including a saved file that already
        holds conflicting rows for one key, raise ``StorageError``. The file
        is only
        created when the first genuine records arrive.
        """
        records = list(records)
        if not all(isinstance(record, WeatherRecord) for record in records):
            raise ValueError("append() accepts WeatherRecord objects only")
        batch: dict[tuple, WeatherRecord] = {}
        for record in records:
            earlier = batch.setdefault(record.key, record)
            if earlier != record:
                raise ValueError(
                    "conflicting values for one record key in"
                    f" {record.city_id}"
                )
        if not batch:
            return 0

        with self.__lock:
            saved = self._read_all()
            existing = {record.key: record for record in saved}
            new_rows = []
            new_records = []
            for key, record in batch.items():
                if key in existing:
                    if existing[key] != record:
                        raise ValueError(
                            f"{record.city_id} record already saved with"
                            " different values"
                        )
                    continue
                new_rows.append(record.to_csv_row())
                new_records.append(record)
            if new_rows:
                self._write_with_new_rows(new_rows)
                # Publish the validated snapshot only after the atomic save.
                # The next read still compares actual bytes, so changes made
                # by another store/editor are never hidden by this cache.
                prefix = self.__validated_raw
                if prefix is None:
                    prefix = _csv_text([
                        dict(zip(RECORD_FIELDS, RECORD_FIELDS))
                    ])
                self.__validated_raw = prefix + _csv_text(new_rows)
                self.__validated_records = tuple(saved + new_records)
        return len(new_rows)

    def _write_with_new_rows(self, rows: list[dict[str, str]]) -> None:
        directory = self._path.parent
        temp_name = None
        try:
            directory.mkdir(parents=True, exist_ok=True)
            candidate = directory / (
                f".{self._path.name}.{secrets.token_hex(8)}.tmp"
            )
            # os.open (not tempfile) so a first file gets the umask's normal
            # permissions instead of tempfile's owner-only 0o600. O_EXCL
            # never reuses an existing file, and only a file created here
            # is ever cleaned up.
            descriptor = os.open(
                candidate,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | getattr(os, "O_BINARY", 0),
                0o666,
            )
            temp_name = candidate
            with os.fdopen(descriptor, "wb") as handle:
                if self._path.exists():
                    with self._path.open("rb") as current:
                        shutil.copyfileobj(current, handle)
                else:
                    handle.write(
                        _csv_text([dict(zip(RECORD_FIELDS, RECORD_FIELDS))])
                    )
                handle.write(_csv_text(rows))
                handle.flush()
                os.fsync(handle.fileno())
            if self._path.exists():
                # Keep the saved file's permissions across the swap.
                shutil.copymode(self._path, temp_name)
            _retry_file_lock(os.replace, temp_name, self._path)
            temp_name = None
        except OSError as error:
            raise StorageError(
                f"Could not save weather records to {self._path.name}:"
                f" {error.strerror or error}", os_error=error
            ) from None
        finally:
            if temp_name is not None:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass

    # -- reading

    def load(
        self, city_id: str | None = None, kind: str | None = None
    ) -> list[WeatherRecord]:
        """Return saved records in file order, optionally filtered."""
        if kind is not None and kind not in WEATHER_KINDS:
            raise ValueError("kind must be 'current', 'forecast' or None")
        if city_id is not None and (
            not isinstance(city_id, str) or not city_id.strip()
        ):
            raise ValueError("city_id must be non-empty text or None")
        with self.__lock:
            records = self._read_all()
        return [
            record
            for record in records
            if (city_id is None or record.city_id == city_id)
            and (kind is None or record.kind == kind)
        ]

    def latest_forecast(self, city_id: str) -> list[WeatherRecord]:
        """The newest saved forecast response for one city, ordered by valid
        time.

        Only one fetch group is returned; periods are never stitched
        together
        from different forecast issues. An empty list means no forecast
        saved.
        """
        if not isinstance(city_id, str) or not city_id.strip():
            raise ValueError("city_id must be non-empty text")
        groups: dict[str, list[WeatherRecord]] = {}
        for record in self.load(city_id=city_id, kind="forecast"):
            groups.setdefault(record.fetch_id, []).append(record)
        if not groups:
            return []
        # max() keeps the first maximum, so iterate newest-saved first for
        # ties.
        newest = max(
            reversed(list(groups.values())),
            key=lambda group: group[0].retrieved_at_utc,
        )
        return sorted(newest)

    def _read_all(self) -> list[WeatherRecord]:
        try:
            raw = _retry_file_lock(self._path.read_bytes)
        except FileNotFoundError:
            self.__validated_raw = None
            self.__validated_records = ()
            return []
        except OSError as error:
            raise StorageError(
                f"Could not read {self._path.name}: {error.strerror or error}",
                os_error=error,
            ) from None
        # WeatherRecord values are frozen. Return a fresh list so callers
        # cannot mutate the validated sequence. Compare contents, not mtime:
        # even same-size edits or a restored timestamp must be revalidated.
        if raw == self.__validated_raw:
            return list(self.__validated_records)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise StorageError(
                f"{self._path.name} is not valid UTF-8", invalid_file=True
            ) from None
        if text and not text.endswith("\n"):
            raise StorageError(
                f"{self._path.name} ends with an incomplete row; restore it"
                " from Git before saving more records", invalid_file=True
            )
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if tuple(reader.fieldnames or ()) != RECORD_FIELDS:
            raise StorageError(
                f"{self._path.name} does not have the expected header",
                invalid_file=True,
            )
        # Duplicate keys are checked here so no caller (load, latest_forecast
        # or
        # append's idempotency check) can use an inconsistent file. A row that
        # repeats an earlier row exactly is the same genuine record: it is
        # returned once. A row with the same key but different values is a
        # conflict: reading stops. The file itself is never modified here.
        records: list[WeatherRecord] = []
        first_line: dict[tuple, tuple[int, WeatherRecord]] = {}
        for row in reader:
            line = reader.line_num
            try:
                record = WeatherRecord.from_csv_row(row)
            except ValueError as error:
                raise StorageError(
                    f"{self._path.name} line {line}: {error}",
                    invalid_file=True,
                ) from None
            earlier = first_line.get(record.key)
            if earlier is None:
                first_line[record.key] = (line, record)
                records.append(record)
            elif earlier[1] != record:
                raise StorageError(
                    f"{self._path.name} line {line}: conflicting values for"
                    f" the record on line {earlier[0]} ({record.city_id}"
                    f" {record.kind} valid at"
                    f" {format_utc(record.valid_at_utc)}, fetch"
                    f" {record.fetch_id}); resolve the file manually before"
                    " using it", invalid_file=True
                )
        self.__validated_raw = raw
        self.__validated_records = tuple(records)
        return records


def _csv_text(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=RECORD_FIELDS, lineterminator="\n"
    )
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
