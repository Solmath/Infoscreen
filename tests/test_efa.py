from datetime import datetime

import httpx
import respx

from infoscreen.efa import EFA

EFA_URL = "https://example.invalid/vvs"


@respx.mock
def test_get_departures_parses_json_served_as_html_content_type():
    route = respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(
            200,
            content=b'{"departureList": []}',
            headers={"content-type": "text/html"},
        )
    )

    efa = EFA(EFA_URL)
    result = efa.get_departures("Stuttgart", "Vaihingen", datetime(2026, 1, 1, 12, 0))

    assert result == {"departureList": []}
    sent_data = route.calls.last.request.read().decode()
    assert "place_dm=Stuttgart" in sent_data
    assert "name_dm=Vaihingen" in sent_data


@respx.mock
def test_get_departures_omits_place_when_none():
    route = respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )

    efa = EFA(EFA_URL)
    efa.get_departures(None, "Vaihingen", datetime(2026, 1, 1, 12, 0))

    sent_data = route.calls.last.request.read().decode()
    assert "place_dm" not in sent_data


@respx.mock
def test_get_departures_does_not_leak_state_between_calls():
    respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )

    efa = EFA(EFA_URL)
    efa.get_departures("Stuttgart", "Vaihingen", datetime(2026, 1, 1, 12, 0))
    efa.get_departures(None, "Rohr", datetime(2026, 1, 1, 12, 5))

    sent_data = respx.calls.last.request.read().decode()
    assert "place_dm" not in sent_data
    assert "name_dm=Rohr" in sent_data
