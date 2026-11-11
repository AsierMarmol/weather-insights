"""Configuration checks use temporary files and dummy credentials only."""

import importlib

import pytest
from weather_app import config


def test_import_does_not_read_credentials(monkeypatch):
    def unexpected_load(*args, **kwargs):
        pytest.fail("Import must not read credential files")
    monkeypatch.setattr("dotenv.load_dotenv", unexpected_load)
    try:
        importlib.reload(config)
    finally:
        # Restore the module's function binding as well as the patched provider.
        monkeypatch.undo()
        importlib.reload(config)


@pytest.mark.parametrize("contents", [None, "OPENWEATHER_API_KEY=\n", "OPENWEATHER_API_KEY=   \n"])
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


def test_file_loading_is_independent_of_working_directory(tmp_path, monkeypatch):
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
