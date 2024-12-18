from flask import (
    Blueprint, render_template
)
from datetime import datetime
from zoneinfo import ZoneInfo
from EFA_API import EFA
# from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('departure', __name__, url_prefix='/departure')

@bp.route('/departure_table', methods=('GET', 'POST'))
async def departure_table():
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    efa = EFA("https://efa.vvs.de/vvs/")
    departures = await efa.get_departures("Stuttgart", "Vaihingen", now)
    
    rows = []
    for departure in departures.get("departureList", []):
        servingLine = departure["servingLine"]  
        
        dateTime = departure["dateTime"]
        dateTime = f"{dateTime["hour"]}:{str(dateTime["minute"]).zfill(2)}"
        
        realTime = dateTime       
        cancelled = False
        delay = ""
        
        if servingLine["realtime"] == "1":
            # Todo: Check if this should be "realtimeStatus" instead of "realtimeTripStatus"
            if "realtimeStatus" in departure:
                if departure["realtimeStatus"] == "DEPARTURE_CANCELLED" or departure["realtimeStatus"] == "TRIP_CANCELLED":
                    cancelled = True
            
            if not cancelled:
                if int(servingLine["delay"]) != 0:
                    if int(servingLine["delay"]) > 0:
                        delay = "+" + servingLine["delay"]
                    else:
                        delay = servingLine["delay"]
                        
                    realTime = f"{departure['realDateTime']['hour']}:{str(departure['realDateTime']['minute']).zfill(2)}"
                
        row = {
            "number": servingLine["number"],
            "destination": servingLine["direction"],
            "direction": servingLine["liErgRiProj"]["direction"],
            "dateTime": dateTime,
            "realTime": realTime,
            "delay": delay,
            "cancelled": cancelled,
            "countdown": departure["countdown"]
        }
        rows.append(row)
        
    return render_template('departure_table.html', rows=rows)
    