from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, abort, current_app, render_template, request

from .efa import EFA, EFAError

bp = Blueprint("departure", __name__)


def _departure_ts(now, countdown):
    # absolute timestamp lets the client tick the countdown live between polls
    try:
        return (now + timedelta(minutes=int(countdown))).isoformat()
    except TypeError, ValueError:
        return None


@bp.route("/departure")
def departure():
    return render_template(
        "departure.html", stations=current_app.config["EFA_STATIONS"]
    )


@bp.route("/departure_table", methods=("GET", "POST"))
def departure_table():
    stations = current_app.config["EFA_STATIONS"]
    station = request.args.get("station", stations[0])
    if station not in stations:
        abort(400, description=f"Unknown station: {station}")

    now = datetime.now(ZoneInfo(current_app.config["EFA_TIMEZONE"]))
    efa = EFA(
        current_app.config["EFA_URL"],
        timeout=current_app.config["EFA_TIMEOUT"],
        cache_ttl=current_app.config["EFA_CACHE_TTL"],
    )

    try:
        departures = efa.get_departures(current_app.config["EFA_PLACE"], station, now)
    except EFAError:
        current_app.logger.exception("Failed to fetch departures from EFA")
        return render_template("departures_unavailable.html")

    rowsH = []
    rowsR = []
    for departure in departures.get("departureList", []):
        servingLine = departure["servingLine"]

        dt = departure["dateTime"]
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

        row = {
            "number": servingLine["number"],
            "destination": servingLine["direction"],
            "dateTime": dateTime,
            "realTime": realTime,
            "delay": delay,
            "cancelled": cancelled,
            "countdown": departure["countdown"],
            "departureTs": _departure_ts(now, departure["countdown"]),
        }

        if servingLine["liErgRiProj"]["direction"] == "R":
            rowsR.append(row)
        elif servingLine["liErgRiProj"]["direction"] == "H":
            rowsH.append(row)

    return render_template("departure_tables.html", rowsR=rowsR, rowsH=rowsH)
