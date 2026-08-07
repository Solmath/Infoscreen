import pytest
from flask import Flask

from infoscreen import config


def _app_with_env(monkeypatch, **env):
    monkeypatch.delenv("EFA_URL", raising=False)
    monkeypatch.delenv("EFA_PLACE", raising=False)
    monkeypatch.delenv("EFA_STATIONS", raising=False)
    monkeypatch.delenv("EFA_TIMEZONE", raising=False)
    monkeypatch.delenv("EFA_TIMEOUT", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return Flask(__name__)


def test_init_app_fails_fast_when_efa_url_missing(monkeypatch):
    app = _app_with_env(monkeypatch, EFA_PLACE="TestCity", EFA_STATIONS="Central")

    with pytest.raises(config.MissingConfigError, match="EFA_URL"):
        config.init_app(app)


def test_init_app_fails_fast_when_stations_empty(monkeypatch):
    app = _app_with_env(
        monkeypatch,
        EFA_URL="https://example.invalid/efa",
        EFA_PLACE="TestCity",
        EFA_STATIONS="  , ,",
    )

    with pytest.raises(config.MissingConfigError, match="EFA_STATIONS"):
        config.init_app(app)


def test_init_app_parses_stations_and_defaults_timezone(monkeypatch):
    app = _app_with_env(
        monkeypatch,
        EFA_URL="https://example.invalid/efa",
        EFA_PLACE="TestCity",
        EFA_STATIONS="Central, North ,East",
    )

    config.init_app(app)

    assert app.config["EFA_STATIONS"] == ["Central", "North", "East"]
    assert app.config["EFA_TIMEZONE"] == "UTC"
    assert app.config["EFA_TIMEOUT"] == 5.0


def test_init_app_reads_timeout_and_cache_ttl_overrides(monkeypatch):
    app = _app_with_env(
        monkeypatch,
        EFA_URL="https://example.invalid/efa",
        EFA_PLACE="TestCity",
        EFA_STATIONS="Central",
        EFA_TIMEOUT="2.5",
        EFA_CACHE_TTL="60",
    )

    config.init_app(app)

    assert app.config["EFA_TIMEOUT"] == 2.5
