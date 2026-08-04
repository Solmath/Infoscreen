import json
import time

import httpx

# Reused across requests: avoids a new TLS handshake + connection per call.
_client = httpx.Client()

# Module-level so the TTL cache is shared across all EFA instances/requests
# in this process, instead of one upstream call per client poll.
_cache = {}


class EFAError(RuntimeError):
    """Raised when the upstream EFA API cannot be reached or returns unusable data."""


class EFA:
    def __init__(self, url, timeout=5.0, cache_ttl=30.0, proximity_search=False):
        self.dm_url = url + "/XML_DM_REQUEST"
        self.proximity_search = proximity_search
        self.timeout = timeout
        self.cache_ttl = cache_ttl

    def get_departures(self, place, name, ts):
        cache_key = (self.dm_url, place, name)
        cached = _cache.get(cache_key)
        if cached is not None:
            expires_at, departures = cached
            if expires_at > time.monotonic():
                return departures
            del _cache[cache_key]

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

        _cache[cache_key] = (time.monotonic() + self.cache_ttl, departures)
        return departures
