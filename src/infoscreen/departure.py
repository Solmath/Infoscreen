from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request

from .efa import EFA

bp = Blueprint("departure", __name__)


@bp.route("/departure")
def departure():
    return render_template("departure.html")


@bp.route("/departure_table", methods=("GET", "POST"))
async def departure_table():
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    efa = EFA("https://efa.vvs.de/vvs/")

    station = request.args.get("station", "Vaihingen")
    # Use Vaihingen as default station

    departures = await efa.get_departures("Stuttgart", station, now)

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
        }

        if servingLine["liErgRiProj"]["direction"] == "R":
            rowsR.append(row)
        elif servingLine["liErgRiProj"]["direction"] == "H":
            rowsH.append(row)

    return render_template("departure_tables.html", rowsR=rowsR, rowsH=rowsH)
