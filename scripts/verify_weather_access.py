"""P2.3 bounded provider check; not the production client or scheduled
collector.

Run from the project: uv run --locked python
scripts/verify_weather_access.py
Successful responses are retained as genuine verification fetches. Never
print
request URLs, response bodies for errors, credentials or request exceptions.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import sleep
from zoneinfo import ZoneInfo

import requests
from weather_app.config import get_api_key

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://api.openweathermap.org/data/2.5"
UTC = timezone.utc
DATA = ROOT / "data" / "weather"
SUPPORTED_FORECAST_HOURS = tuple(24 * days for days in range(1, 6))


def redact(value, secret):
    """Remove credentials even if a provider unexpectedly echoes them."""
    if isinstance(value, dict):
        return {
            k: redact(v, secret)
            for k, v in value.items()
            if k.lower()
            not in {"appid", "api_key", "openweather_api_key", "authorization"}
        }
    if isinstance(value, list):
        return [redact(v, secret) for v in value]
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]") if secret else value
    return value


def finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def name_key(value):
    """Ignore accents, punctuation and case, but do not invent city aliases."""
    plain = unicodedata.normalize("NFKD", value)
    return "".join(
        c
        for c in plain.casefold()
        if c.isalnum() and not unicodedata.combining(c)
    )


def location_check(
    payload,
    endpoint,
    latitude,
    longitude,
    catalog_name,
    accepted_names=(),
    expected_provider_id=None,
):
    payload = payload if isinstance(payload, dict) else {}
    location = payload.get("city") if endpoint == "forecast" else payload
    location = location if isinstance(location, dict) else {}
    coord = location.get("coord")
    coord = coord if isinstance(coord, dict) else {}
    system = payload.get("sys")
    system = system if isinstance(system, dict) else {}
    name = location.get("name", "")
    country = (
        location.get("country")
        if endpoint == "forecast"
        else system.get("country")
    )
    lat, lon = coord.get("lat"), coord.get("lon")
    distance = None
    if (
        finite_number(lat)
        and finite_number(lon)
        and -90 <= lat <= 90
        and -180 <= lon <= 180
    ):
        phi1, phi2 = math.radians(latitude), math.radians(lat)
        dphi, dlambda = phi2 - phi1, math.radians(lon - longitude)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        distance = 6371.0088 * 2 * math.asin(math.sqrt(min(1, max(0, a))))
    matches = isinstance(name, str) and name_key(name) == name_key(
        catalog_name
    )
    accepted = isinstance(name, str) and name_key(name) in {
        name_key(n) for n in accepted_names
    }
    provider_id = location.get("id")
    identity_matches = (
        expected_provider_id is None or provider_id == expected_provider_id
    )
    nearby = distance is not None and distance <= 10
    return {
        "catalog_name": catalog_name,
        "provider_name": name,
        "provider_country": country,
        "name_matches_normalized": matches,
        "distance_from_requested_km": (
            round(distance, 3) if distance is not None else None
        ),
        "within_10km": nearby,
        "accepted_provider_alias": accepted and not matches,
        "provider_id": provider_id,
        "provider_id_matches": identity_matches,
        "review_required": not (
            (matches or accepted)
            and country == "ES"
            and nearby
            and identity_matches
        ),
    }


def request_parameters(city, override):
    """Use a documented city-specific ID only when coordinates misidentify it.
    """
    if "request_parameters" in override:
        params = override["request_parameters"]
        if (
            set(params) != {"id"}
            or not isinstance(params["id"], int)
            or isinstance(params["id"], bool)
            or params["id"] <= 0
        ):
            raise ValueError("Invalid provider city-ID override")
        return params.copy()
    return {"lat": float(city["latitude"]), "lon": float(city["longitude"])}


def valid_reading(item, forecast=False):
    if not isinstance(item, dict):
        return False
    main, wind = item.get("main", {}), item.get("wind", {})
    if not isinstance(main, dict) or not isinstance(wind, dict):
        return False
    valid = (
        isinstance(item.get("dt"), int)
        and not isinstance(item.get("dt"), bool)
        and finite_number(main.get("temp"))
        and finite_number(wind.get("speed"))
        and wind["speed"] >= 0
    )
    if forecast:
        valid = (
            valid and finite_number(item.get("pop")) and 0 <= item["pop"] <= 1
        )
    return valid


def coverage(payload, run_at):
    """Verify complete native forecast timestamps for the agreed daytime
    windows.
    """
    periods = payload.get("list", []) if isinstance(payload, dict) else []
    if not isinstance(periods, list) or not all(
        valid_reading(p, True) for p in periods
    ):
        return {"valid_required_fields": False}
    timestamps = [p["dt"] for p in periods]
    if not timestamps:
        return {"valid_required_fields": False}
    madrid = ZoneInfo("Europe/Madrid")
    result = {
        "valid_required_fields": True,
        "period_count": len(periods),
        "unique_sorted_3h_grid": (
            timestamps == sorted(set(timestamps))
            and all(t % 10800 == 0 for t in timestamps)
            and all(b - a == 10800 for a, b in zip(timestamps, timestamps[1:]))
        ),
    }
    first = (int(run_at.timestamp()) // 10800 + 1) * 10800
    for hours in SUPPORTED_FORECAST_HOURS:
        end = int((run_at + timedelta(hours=hours)).timestamp())
        expected = [
            t
            for t in range(first, end + 1, 10800)
            if 9 <= datetime.fromtimestamp(t, UTC).astimezone(madrid).hour < 18
        ]
        present = set(timestamps)
        result[f"daytime_{hours}h"] = {
            "expected_periods": len(expected),
            "complete": bool(expected) and set(expected) <= present,
        }
    return result


def probe(session, endpoint, parameters, key, label, run_id, city_id=None):
    # Each invocation performs exactly one attempt. No hidden retry or
    # redirect.
    params = {**parameters, "appid": key, "units": "metric", "lang": "en"}
    try:
        response = session.get(
            f"{BASE}/{endpoint}",
            params=params,
            timeout=(5, 20),
            allow_redirects=False,
        )
    except requests.Timeout:
        return {"check": label, "result": "timeout"}, None
    except requests.ConnectionError:
        return {"check": label, "result": "connection_error"}, None
    except requests.RequestException:
        return {"check": label, "result": "request_error"}, None
    retrieved_at = datetime.now(UTC).isoformat()
    status = response.status_code
    summary = {"check": label, "http_status": status}
    if status != 200:
        summary["result"] = "http_error"
        return summary, None
    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError:
        summary["result"] = "invalid_json"
        return summary, None
    if not isinstance(payload, dict):
        summary["result"] = "invalid_data"
        return summary, None
    payload = redact(payload, key)
    record = {
        "source": "openweathermap",
        "purpose": "P2.3 live access verification",
        "run_id": run_id,
        "city_id": city_id,
        "kind": "current" if endpoint == "weather" else "forecast",
        "retrieved_at_utc": retrieved_at,
        "payload": payload,
    }
    try:
        # Serialize first so invalid numbers cannot leave an incomplete log
        # line.
        line = json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n"
    except (TypeError, ValueError):
        summary["result"] = "invalid_data"
        return summary, None
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        with (DATA / "api_verification_fetches.jsonl").open(
            "a", encoding="utf-8"
        ) as f:
            f.write(line)
    except OSError:
        summary["result"] = "storage_error"
        return summary, None
    summary["result"] = "saved_success"
    summary["city_id"] = city_id
    return summary, payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-cities",
        action="store_true",
        help=(
            "Check current/forecast for every catalog city; omit deliberate"
            " error diagnostics"
        ),
    )
    args = parser.parse_args(argv)
    try:
        key = get_api_key()
    except ValueError:
        print(
            "OPENWEATHER_API_KEY is missing. Configure it locally; do not"
            " paste it into chat."
        )
        return 1
    with (ROOT / "data/reference/destinations.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        catalog = list(csv.DictReader(f))
    overrides_path = ROOT / "data/reference/weather_location_overrides.json"
    overrides = (
        json.loads(overrides_path.read_text(encoding="utf-8"))["locations"]
        if overrides_path.exists()
        else {}
    )
    selected = (
        catalog
        if args.all_cities
        else [
            next(r for r in catalog if r["city"] == name)
            for name in ("Toledo", "Segovia")
        ]
    )
    if not selected or len({r["city_id"] for r in selected}) != len(selected):
        raise ValueError("Catalog is empty or contains duplicate city IDs")
    for city in selected:
        lat, lon = float(city["latitude"]), float(city["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Invalid catalog coordinates; no request made")
    run_at = datetime.now(UTC)
    run_id = run_at.isoformat()
    report = {
        "run_started_at_utc": run_id,
        "scope": (
            "all catalog cities"
            if args.all_cities
            else "two catalog cities; at most six HTTP requests"
        ),
        "catalog_city_count": len(selected),
        "expected_http_requests": (
            2 * len(selected) + (0 if args.all_cities else 2)
        ),
        "checks": [],
        "credential_value_recorded": False,
    }
    stopped = False
    with requests.Session() as session:
        for index, city in enumerate(selected, 1):
            name = city["city"]
            override = overrides.get(city["city_id"], {})
            lat, lon = float(city["latitude"]), float(city["longitude"])
            for endpoint in ("weather", "forecast"):
                summary, payload = probe(
                    session,
                    endpoint,
                    request_parameters(city, override),
                    key,
                    f"{name}:{endpoint}",
                    run_id,
                    city["city_id"],
                )
                if payload is not None:
                    summary["schema_check"] = (
                        coverage(payload, run_at)
                        if endpoint == "forecast"
                        else {"valid_required_fields": valid_reading(payload)}
                    )
                    summary["location_check"] = location_check(
                        payload,
                        endpoint,
                        lat,
                        lon,
                        name,
                        override.get("accepted_names", ()),
                        override.get("expected_provider_id"),
                    )
                report["checks"].append(summary)
                if not args.all_cities:
                    print(json.dumps(summary), flush=True)
                if (
                    summary.get("http_status") in {401, 403, 429}
                    or summary.get("result") == "storage_error"
                ):
                    report["stopped_for_status"] = summary.get("http_status")
                    report["stopped_for_result"] = summary["result"]
                    stopped = True
                    break
                sleep(1.5)
            if args.all_cities and (
                index % 10 == 0 or index == len(selected) or stopped
            ):
                print(
                    json.dumps(
                        {
                            "cities_attempted": index,
                            "of": len(selected),
                            "requests_completed": len(report["checks"]),
                        }
                    ),
                    flush=True,
                )
            if stopped:
                break
        # Safe diagnostics only; catalog requests use coordinates, not this
        # legacy city lookup.
        diagnostics = (
            ()
            if args.all_cities or stopped
            else (
                (
                    "invalid_key",
                    {"lat": 39.8581, "lon": -4.0226},
                    "p23-deliberately-invalid-key",
                ),
                ("unknown_city", {"q": "P23NoSuchSpanishCity9f3c,ES"}, key),
            )
        )
        for label, parameters, probe_key in diagnostics:
            summary, _ = probe(
                session, "weather", parameters, probe_key, label, run_id
            )
            report["checks"].append(summary)
            print(json.dumps(summary))
            sleep(1.5)
    report["run_finished_at_utc"] = datetime.now(UTC).isoformat()
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        with (DATA / "api_verification_runs.jsonl").open(
            "a", encoding="utf-8"
        ) as f:
            f.write(json.dumps(report, ensure_ascii=False) + "\n")
    except OSError:
        print(
            json.dumps(
                {
                    "result": "storage_error",
                    "message": "Could not save verification summary.",
                }
            )
        )
        return 1
    live = report["checks"][: 2 * len(selected)]
    passed = len(live) == 2 * len(selected) and all(
        c.get("result") == "saved_success"
        and c.get("schema_check", {}).get("valid_required_fields")
        for c in live
    )
    for c in live:
        if c["check"].endswith(":forecast"):
            s = c.get("schema_check", {})
            passed = (
                passed
                and s.get("unique_sorted_3h_grid", False)
                and all(
                    s.get(f"daytime_{h}h", {}).get("complete", False)
                    for h in SUPPORTED_FORECAST_HOURS
                )
            )
    diagnostics = report["checks"][2 * len(selected):]
    errors_pass = args.all_cities or [
        c.get("http_status") for c in diagnostics
    ] == [401, 404]
    review_count = sum(
        c.get("location_check", {}).get("review_required", False) for c in live
    )
    print(
        json.dumps(
            {
                "access_and_required_fields_pass": bool(passed),
                "expected_error_statuses_pass": errors_pass,
                "location_checks_requiring_review": review_count,
                "successful_fetches_this_run": sum(
                    c.get("result") == "saved_success"
                    for c in report["checks"]
                ),
            }
        )
    )
    return 0 if passed and errors_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
