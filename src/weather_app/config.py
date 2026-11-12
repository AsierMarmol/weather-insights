"""Local configuration: private credentials and shared reference settings.

Credentials are read only when an API operation needs them, never at import.
Reference files are validated when loaded so a damaged file fails clearly
instead of silently changing product defaults or provider requests.
"""

import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "variables.env"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
PRODUCT_DEFAULTS_FILE = REFERENCE_DIR / "product_defaults.json"
LOCATION_OVERRIDES_FILE = REFERENCE_DIR / "weather_location_overrides.json"

_SEASONS = ("Winter", "Spring", "Summer", "Autumn")


def get_api_key() -> str:
    """Respect process environment precedence; never include a key in errors."""
    load_dotenv(ENV_FILE, override=False)
    key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "OPENWEATHER_API_KEY is not set. Copy variables.env.example to "
            "variables.env and fill in your own key."
        )
    return key


def _read_json(path: Path, label: str) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"Cannot read {label} ({Path(path).name}): {error.strerror}") from None
    except json.JSONDecodeError:
        raise ValueError(f"{label} ({Path(path).name}) is not valid JSON") from None
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def _finite(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def load_product_defaults(path: Path = PRODUCT_DEFAULTS_FILE) -> dict:
    """Load and validate the initial search settings from product_defaults.json.

    These are editable starting preferences (P2.1), not climate data. The
    returned dictionary is the file content unchanged; Searcher decides how to
    initialize or reset user preferences from it.
    """
    data = _read_json(path, "Product defaults")
    problem = _defaults_problem(data)
    if problem:
        raise ValueError(f"Product defaults are invalid: {problem}")
    return data


def _defaults_problem(data: dict) -> str | None:
    days = data.get("supported_forecast_days")
    if days != [1, 2, 3, 4, 5]:
        return "supported_forecast_days must be [1, 2, 3, 4, 5]"
    if data.get("default_forecast_days") not in days:
        return "default_forecast_days must be one of the supported days"
    seasons = data.get("seasonal_temperature_c")
    if not isinstance(seasons, dict) or set(seasons) != set(_SEASONS):
        return f"seasonal_temperature_c must define {', '.join(_SEASONS)}"
    months: list[int] = []
    for name in _SEASONS:
        season = seasons[name]
        if not isinstance(season, dict):
            return f"{name} must be an object"
        low, high = season.get("min"), season.get("max")
        if not (_finite(low) and _finite(high)) or low > high:
            return f"{name} needs finite min <= max temperatures"
        season_months = season.get("months")
        if not isinstance(season_months, list):
            return f"{name} months must be a list"
        months.extend(season_months)
    if sorted(months) != list(range(1, 13)):
        return "seasons must cover each month exactly once"
    rain = data.get("max_precipitation_probability_percent")
    if not _finite(rain) or not 0 <= rain <= 100:
        return "max_precipitation_probability_percent must be between 0 and 100"
    wind = data.get("max_wind_kmh")
    if not _finite(wind) or wind < 0:
        return "max_wind_kmh must be a non-negative number"
    if data.get("default_activities") != "All" or data.get("default_destination_sizes") != "All":
        return "activity and size filters must default to All"
    count = data.get("recommendation_count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        return "recommendation_count must be a positive whole number"
    if data.get("timezone") != "Europe/Madrid":
        return "timezone must be Europe/Madrid"
    return None


def load_location_overrides(path: Path = LOCATION_OVERRIDES_FILE) -> dict[str, dict]:
    """Return provider overrides keyed by catalog city_id.

    Each entry may contain ``request_parameters`` (only a positive provider
    city ``id``), ``expected_provider_id`` and ``accepted_names``. Other keys
    such as ``reason`` are documentation and are kept as they are.
    """
    data = _read_json(path, "Location overrides")
    locations = data.get("locations")
    if not isinstance(locations, dict):
        raise ValueError("Location overrides must contain a 'locations' object")
    for city_id, entry in locations.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Override for {city_id} must be an object")
        params = entry.get("request_parameters")
        if params is not None and (set(params) != {"id"} or not _positive_int(params["id"])):
            raise ValueError(f"Override for {city_id} may only request a positive city id")
        expected = entry.get("expected_provider_id")
        if expected is not None and not _positive_int(expected):
            raise ValueError(f"Override for {city_id} has an invalid expected_provider_id")
        names = entry.get("accepted_names", [])
        if not isinstance(names, list) or not all(isinstance(n, str) and n.strip() for n in names):
            raise ValueError(f"Override for {city_id} has invalid accepted_names")
    return locations


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
