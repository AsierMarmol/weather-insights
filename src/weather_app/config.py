"""Load private credentials only when an API operation needs them."""

import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / "variables.env"


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
