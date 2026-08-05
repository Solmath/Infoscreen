from datetime import datetime

import httpx
import pytest
import respx

from infoscreen.efa_client import EFA, EFAError

EFA_URL = "https://example.invalid/efa"


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
    result = efa.get_departures("TestCity", "Central", datetime(2026, 1, 1, 12, 0))

    assert result == {"departureList": []}
    sent_data = route.calls.last.request.read().decode()
    assert "place_dm=TestCity" in sent_data
    assert "name_dm=Central" in sent_data


@respx.mock
def test_get_departures_omits_place_when_none():
    route = respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )

    efa = EFA(EFA_URL)
    efa.get_departures(None, "Central", datetime(2026, 1, 1, 12, 0))

    sent_data = route.calls.last.request.read().decode()
    assert "place_dm" not in sent_data


@respx.mock
def test_get_departures_does_not_leak_state_between_calls():
    respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(200, json={"departureList": []})
    )

    efa = EFA(EFA_URL)
    efa.get_departures("TestCity", "Central", datetime(2026, 1, 1, 12, 0))
    efa.get_departures(None, "North", datetime(2026, 1, 1, 12, 5))

    sent_data = respx.calls.last.request.read().decode()
    assert "place_dm" not in sent_data
    assert "name_dm=North" in sent_data


@respx.mock
def test_get_departures_raises_efa_error_on_timeout():
    respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        side_effect=httpx.TimeoutException("timed out")
    )

    efa = EFA(EFA_URL, cache_ttl=0)

    with pytest.raises(EFAError):
        efa.get_departures("TestCity", "Central", datetime(2026, 1, 1, 12, 0))


@respx.mock
def test_get_departures_raises_efa_error_on_5xx():
    respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(return_value=httpx.Response(503))

    efa = EFA(EFA_URL, cache_ttl=0)

    with pytest.raises(EFAError):
        efa.get_departures("TestCity", "Central", datetime(2026, 1, 1, 12, 0))


@respx.mock
def test_get_departures_raises_efa_error_on_invalid_json():
    respx.post(f"{EFA_URL}/XML_DM_REQUEST").mock(
        return_value=httpx.Response(200, content=b"not json")
    )

    efa = EFA(EFA_URL, cache_ttl=0)

    with pytest.raises(EFAError):
        efa.get_departures("TestCity", "Central", datetime(2026, 1, 1, 12, 0))
