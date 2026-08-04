import pytest

import infoscreen.efa
from infoscreen import create_app


@pytest.fixture
def app():
    return create_app(
        {
            "TESTING": True,
            "EFA_URL": "https://example.invalid/efa",
            "EFA_PLACE": "TestCity",
            "EFA_STATIONS": ["Central", "North"],
            "EFA_TIMEZONE": "Europe/Berlin",
            "EFA_TIMEOUT": 5.0,
            "EFA_CACHE_TTL": 30.0,
        }
    )


@pytest.fixture(autouse=True)
def _clear_efa_cache():
    # The TTL cache is module-level (shared across requests by design);
    # reset it between tests so they don't leak state into each other.
    infoscreen.efa._cache.clear()
    yield
    infoscreen.efa._cache.clear()


@pytest.fixture
def client(app):
    return app.test_client()
