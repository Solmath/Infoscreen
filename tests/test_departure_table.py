from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import respx

from infoscreen import departure as departure_module

EFA_DM_URL = "https://example.invalid/efa/XML_DM_REQUEST"


def _departure(*, direction, delay="0", cancelled=False):
    status = "DEPARTURE_CANCELLED" if cancelled else "OK"
    return {
        "servingLine": {
            "number": "S1",
            "direction": "Downtown",
            "realtime": "1",
            "delay": delay,
            "liErgRiProj": {"direction": direction},
        },
        "dateTime": {"hour": "12", "minute": "5"},
        "realDateTime": {"hour": "12", "minute": "8"},
        "realtimeStatus": status,
        "countdown": "10",
    }


@respx.mock
def test_departure_table_renders_rows_from_efa_response(client):
    respx.post(EFA_DM_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "departureList": [
                    _departure(direction="H"),
                    _departure(direction="R", delay="3"),
                ]
            },
        )
    )

    resp = client.get("/departure_table")

    assert resp.status_code == 200
    assert b"S1" in resp.data
    assert b"Downtown" in resp.data
    assert b"data-departure-ts=" in resp.data


@respx.mock
def test_departure_table_handles_no_departures(client):
    respx.post(EFA_DM_URL).mock(return_value=httpx.Response(200, json={}))

    resp = client.get("/departure_table")

    assert resp.status_code == 200


def test_departure_table_rejects_station_outside_allowlist(client):
    resp = client.get("/departure_table?station=NotConfigured")

    assert resp.status_code == 400


@respx.mock
def test_departures_api_returns_flat_line_direction_minutes(client):
    respx.post(EFA_DM_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "departureList": [
                    _departure(direction="H"),
                    _departure(direction="R", delay="3"),
                ]
            },
        )
    )

    resp = client.get("/api/departures?station=Central")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["departures"] == [
        {"line": "S1", "direction": "Downtown", "minutes": 10},
        {"line": "S1", "direction": "Downtown", "minutes": 10},
    ]


@respx.mock
def test_departures_api_defaults_to_first_station_when_missing(client):
    respx.post(EFA_DM_URL).mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )

    resp = client.get("/api/departures")

    assert resp.status_code == 200


def test_departures_api_rejects_station_outside_allowlist(client):
    resp = client.get("/api/departures?station=NotConfigured")

    assert resp.status_code == 400


def test_departure_page_passes_stations_to_alpine_component(client):
    resp = client.get("/departure")

    assert resp.status_code == 200
    assert b'["Central", "North"]' in resp.data
    assert b"alpine.min.js" in resp.data


def test_stations_api_returns_configured_stations(client):
    resp = client.get("/api/stations")

    assert resp.status_code == 200
    assert resp.get_json() == {"stations": ["Central", "North"]}


class _FakeDateTime(datetime):
    """Stand-in for departure.datetime with a controllable now()."""

    current = datetime(2026, 1, 1, 12, 0, tzinfo=ZoneInfo("Europe/Berlin"))

    @classmethod
    def now(cls, tz=None):
        return cls.current


@respx.mock
def test_departures_are_cached_within_ttl(client, monkeypatch):
    route = respx.post(EFA_DM_URL).mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )
    monkeypatch.setattr(departure_module, "datetime", _FakeDateTime)

    client.get("/departure_table")
    client.get("/departure_table")

    assert route.calls.call_count == 1


@respx.mock
def test_departures_refetch_after_ttl_expires(client, monkeypatch):
    route = respx.post(EFA_DM_URL).mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )
    monkeypatch.setattr(departure_module, "datetime", _FakeDateTime)
    _FakeDateTime.current = datetime(
        2026, 1, 1, 12, 0, tzinfo=ZoneInfo("Europe/Berlin")
    )

    client.get("/departure_table")
    _FakeDateTime.current += timedelta(seconds=31)
    client.get("/departure_table")

    assert route.calls.call_count == 2
