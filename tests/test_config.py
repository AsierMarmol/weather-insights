"""Configuration checks use temporary files and dummy credentials only."""

import importlib
import json

import pytest
from weather_app import config


def test_import_does_not_read_credentials(monkeypatch):
    def unexpected_load(*args, **kwargs):
        pytest.fail("Import must not read credential files")

    monkeypatch.setattr("dotenv.load_dotenv", unexpected_load)
    try:
        importlib.reload(config)
    finally:
        # Restore the module's function binding as well as the patched
        # provider.
        monkeypatch.undo()
        importlib.reload(config)


@pytest.mark.parametrize(
    "contents", [None, "OPENWEATHER_API_KEY=\n", "OPENWEATHER_API_KEY=   \n"]
)
def test_missing_or_blank_key_is_explicit(tmp_path, monkeypatch, contents):
    local = tmp_path / "variables.env"
    if contents is not None:
        local.write_text(contents)
    monkeypatch.setattr(config, "ENV_FILE", local)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENWEATHER_API_KEY is not set"):
        config.get_api_key()


def test_environment_wins_over_file(tmp_path, monkeypatch):
    local = tmp_path / "variables.env"
    local.write_text("OPENWEATHER_API_KEY=dummy-file-value\n")
    monkeypatch.setattr(config, "ENV_FILE", local)
    monkeypatch.setenv("OPENWEATHER_API_KEY", "dummy-process-value")
    assert config.get_api_key() == "dummy-process-value"


def test_file_loading_is_independent_of_working_directory(
    tmp_path, monkeypatch
):
    local = tmp_path / "variables.env"
    local.write_text("OPENWEATHER_API_KEY=dummy-file-value\n")
    monkeypatch.setattr(config, "ENV_FILE", local)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    try:
        assert config.get_api_key() == "dummy-file-value"
    finally:
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)


# --- P3.2 reference loaders (real files read-only; damaged copies in tmp_path)


def test_product_defaults_load_and_match_agreed_values():
    defaults = config.load_product_defaults()
    assert defaults["default_forecast_days"] == 3
    assert defaults["seasonal_temperature_c"]["Autumn"] == {
        "months": [9, 10, 11],
        "min": 16,
        "max": 24,
    }
    assert defaults["max_precipitation_probability_percent"] == 30
    assert defaults["max_wind_kmh"] == 25
    assert (
        defaults["default_activities"]
        == defaults["default_destination_sizes"]
        == "All"
    )


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(default_forecast_days=6),
        lambda d: d["seasonal_temperature_c"]["Winter"].update(months=[1, 2]),
        lambda d: d["seasonal_temperature_c"]["Summer"].update(min=31),
        lambda d: d.update(max_precipitation_probability_percent=101),
        lambda d: d.update(max_wind_kmh=True),
        lambda d: d.update(default_activities="Coast"),
    ],
)
def test_damaged_product_defaults_are_rejected(tmp_path, change):
    data = json.loads(config.PRODUCT_DEFAULTS_FILE.read_text(encoding="utf-8"))
    change(data)
    path = tmp_path / "defaults.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Product defaults are invalid"):
        config.load_product_defaults(path)


def test_unreadable_reference_files_fail_clearly(tmp_path):
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        config.load_product_defaults(tmp_path / "bad.json")
    with pytest.raises(ValueError, match="Cannot read"):
        config.load_location_overrides(tmp_path / "missing.json")


def test_location_overrides_keep_lugo_city_id():
    overrides = config.load_location_overrides()
    assert overrides["ES-27028"]["request_parameters"] == {"id": 3117814}
    assert overrides["ES-27028"]["expected_provider_id"] == 3117814
    assert "Lleida" in overrides["ES-25120"]["accepted_names"]


def test_override_may_only_request_a_city_id(tmp_path):
    path = tmp_path / "overrides.json"
    path.write_text(
        json.dumps(
            {"locations": {"ES-27028": {"request_parameters": {"q": "Lugo"}}}}
        )
    )
    with pytest.raises(ValueError, match="positive city id"):
        config.load_location_overrides(path)
