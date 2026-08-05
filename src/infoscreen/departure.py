import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Blueprint, abort, current_app, jsonify, render_template, request

from .efa_client import EFA, EFAError

departure_bp = Blueprint("departure", __name__)

CACHE_TTL_SECONDS = 30
_cache = {}


def _departure_ts(now, minutes):
    # absolute timestamp lets the client tick the countdown live between polls
    try:
        return (now + timedelta(minutes=minutes)).isoformat()
    except TypeError, ValueError:
        return None


def get_departures(station: str, force_refresh: bool = False):

    now = datetime.now(ZoneInfo(current_app.config["EFA_TIMEZONE"]))
    entry = _cache.setdefault(station, {"data": None, "fetched_at": None})
    is_stale = (
        entry["fetched_at"] is None
        or (now - entry["fetched_at"]).total_seconds() > CACHE_TTL_SECONDS
    )

    efa = EFA(
        current_app.config["EFA_URL"],
        timeout=current_app.config["EFA_TIMEOUT"],
    )

    if force_refresh or is_stale or entry["data"] is None:
        try:
            entry["data"] = efa.get_departures(
                current_app.config["EFA_PLACE"], station, now
            )
            entry["fetched_at"] = now
        except EFAError as exc:
            current_app.logger.exception("Failed to fetch departures from EFA")
            return entry["data"] or {}, {
                "error": str(exc),
                "stale": True,
                "fetched_at": entry["fetched_at"].isoformat()
                if entry["fetched_at"]
                else None,
            }

    return entry["data"], {
        "error": None,
        "stale": False,
        "fetched_at": entry["fetched_at"].isoformat() if entry["fetched_at"] else None,
    }


@departure_bp.route("/departure")
def departure():
    return render_template(
        "departure.html", stations=current_app.config["EFA_STATIONS"]
    )


@departure_bp.route("/api/stations")
def stations_api():
    return jsonify({"stations": current_app.config["EFA_STATIONS"]})


def _load_boards_config():
    # Read fresh on every request so the file can be edited/mounted without a restart.
    path = Path(current_app.instance_path) / "boards.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except OSError, json.JSONDecodeError:
        current_app.logger.exception("Failed to read boards config from %s", path)
        return []


@departure_bp.route("/api/boards")
def boards_api():
    return jsonify({"boards": _load_boards_config()})


def _parse_departure_row(departure, now):
    servingLine = departure["servingLine"]

    dt = departure["dateTime"]
    minutes = int(departure["countdown"])
    dateTime = f"{dt['hour']}:{str(dt['minute']).zfill(2)}"

    realTime = dateTime
    cancelled = False
    delay = ""

    if servingLine["realtime"] == "1":
        if "realtimeStatus" in departure and (
            departure["realtimeStatus"] == "DEPARTURE_CANCELLED"
            or departure["realtimeStatus"] == "TRIP_CANCELLED"
        ):
            cancelled = True
        else:
            if int(servingLine["delay"]) != 0:
                if int(servingLine["delay"]) > 0:
                    delay = "+" + servingLine["delay"]
                else:
                    delay = servingLine["delay"]

                realTime = f"{departure['realDateTime']['hour']}:{str(departure['realDateTime']['minute']).zfill(2)}"

    return {
        "line": servingLine["number"],
        "destination": servingLine["direction"],
        "direction": servingLine["liErgRiProj"]["direction"],
        "dateTime": dateTime,
        "realTime": realTime,
        "delay": delay,
        "cancelled": cancelled,
        "minutes": minutes,
        "departureTs": _departure_ts(now, minutes),
    }


@departure_bp.route("/api/departures")
def departures_api():
    station = request.args.get("station", current_app.config["EFA_STATIONS"][0])

    data, meta = get_departures(station=station)
    now = datetime.fromisoformat(meta["fetched_at"]) if meta["fetched_at"] else None

    departures = [_parse_departure_row(d, now) for d in data.get("departureList") or []]

    return jsonify({"departures": departures, "meta": meta, "server_time": time.time()})


@departure_bp.route("/departure_table", methods=("GET", "POST"))
def departure_table():
    stations = current_app.config["EFA_STATIONS"]
    station = request.args.get("station", stations[0])
    if station not in stations:
        abort(400, description=f"Unknown station: {station}")

    departures, meta = get_departures(station=station)
    now = datetime.fromisoformat(meta["fetched_at"]) if meta["fetched_at"] else None

    rows = [_parse_departure_row(d, now) for d in departures.get("departureList") or []]
    rowsR = [row for row in rows if row["direction"] == "R"]
    rowsH = [row for row in rows if row["direction"] == "H"]

    return render_template("departure_tables.html", rowsR=rowsR, rowsH=rowsH)
