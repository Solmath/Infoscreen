import pytest

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
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
