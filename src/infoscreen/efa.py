import json

import httpx

# Reused across requests: avoids a new TLS handshake + connection per call.
_client = httpx.Client()


class EFA:
    def __init__(self, url, proximity_search=False):
        self.dm_url = url + "/XML_DM_REQUEST"
        self.proximity_search = proximity_search

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

        response = _client.post(self.dm_url, data=post_data)
        # EFA may return JSON with a text/html Content-Type, which response.json() does not like.
        return json.loads(response.text)
