"""Runtime configuration loaded from environment variables.

Keeps every location detail (transit operator endpoint, place, stations,
timezone) out of the codebase; see the project readme for the required
variables.
"""

import os


class MissingConfigError(RuntimeError):
    """Raised when a required environment variable is missing or empty."""


def _require(name):
    value = os.environ.get(name)
    if not value:
        raise MissingConfigError(f"{name} environment variable is required")
    return value


def init_app(app):
    """Populate app.config with EFA_* settings, failing fast if incomplete."""
    app.config["EFA_URL"] = _require("EFA_URL")
    app.config["EFA_PLACE"] = _require("EFA_PLACE")

    stations = [s.strip() for s in _require("EFA_STATIONS").split(",") if s.strip()]
    if not stations:
        raise MissingConfigError("EFA_STATIONS must contain at least one station")
    app.config["EFA_STATIONS"] = stations

    app.config["EFA_TIMEZONE"] = os.environ.get("EFA_TIMEZONE", "UTC")
    app.config["EFA_TIMEOUT"] = float(os.environ.get("EFA_TIMEOUT", "5"))
    app.config["EFA_CACHE_TTL"] = float(os.environ.get("EFA_CACHE_TTL", "30"))
