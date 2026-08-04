import httpx
import respx

EFA_DM_URL = "https://example.invalid/efa/XML_DM_REQUEST"


def _departure(*, direction, delay="0", cancelled=False):
    status = "DEPARTURE_CANCELLED" if cancelled else "OK"
    return {
        "servingLine": {
            "number": "S1",
            "direction": "Kirchheim",
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
    assert b"Kirchheim" in resp.data


@respx.mock
def test_departure_table_handles_no_departures(client):
    respx.post(EFA_DM_URL).mock(return_value=httpx.Response(200, json={}))

    resp = client.get("/departure_table")

    assert resp.status_code == 200


def test_departure_table_rejects_station_outside_allowlist(client):
    resp = client.get("/departure_table?station=NotConfigured")

    assert resp.status_code == 400
