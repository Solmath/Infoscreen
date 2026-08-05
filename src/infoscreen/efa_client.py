import json

import httpx

# Reused across requests: avoids a new TLS handshake + connection per call.
_client = httpx.Client()


class EFAError(RuntimeError):
    """Raised when the upstream EFA API cannot be reached or returns unusable data."""


def _dm_error(dm):
    # EFA reports an unresolved stop name via dm.message entries instead of an HTTP error.
    messages = dm.get("message") or []
    if isinstance(messages, dict):
        messages = [messages]
    for message in messages:
        if message.get("name") == "error":
            return message.get("value")
    return None


class EFA:
    def __init__(self, url, timeout=5.0, cache_ttl=30.0, proximity_search=False):
        self.dm_url = url + "/XML_DM_REQUEST"
        self.proximity_search = proximity_search
        self.timeout = timeout

    def get_departures(self, place, name, ts):
        post_data = {
            "language": "de",
            "mode": "direct",
            "outputFormat": "JSON",
            "type_dm": "stop",
            "useProxFootSearch": "1" if self.proximity_search else "0",
            "useRealtime": "1",
            "itdDateDay": ts.day,
            "itdDateMonth": ts.month,
            "itdDateYear": ts.year,
            "itdTimeHour": ts.hour,
            "itdTimeMinute": ts.minute,
            "name_dm": name,
        }
        if place is not None:
            post_data["place_dm"] = place

        try:
            response = _client.post(self.dm_url, data=post_data, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EFAError(f"EFA request to {self.dm_url} failed: {exc}") from exc

        try:
            # EFA may return JSON with a text/html Content-Type, which response.json() does not like.
            departures = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise EFAError(f"EFA returned invalid JSON from {self.dm_url}") from exc

        error = _dm_error(departures.get("dm", {}))
        if error:
            raise EFAError(f"EFA rejected stop {name!r}: {error}")

        return departures
