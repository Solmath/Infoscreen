import pytest

from infoscreen import create_app
from infoscreen import departure as departure_module


@pytest.fixture(autouse=True)
def clear_departure_cache():
    departure_module._cache.clear()
    yield
    departure_module._cache.clear()


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
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
