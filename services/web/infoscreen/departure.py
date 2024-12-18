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
    
    dateTime = departures["dateTime"]
    dateTime = f"{dateTime["hour"]}:{str(dateTime["minute"]).zfill(2)}"       
    
    rows = []
    for departure in departures.get("departureList", []):
        row = {
            "number": departure["servingLine"]["number"],
            "direction": departure["servingLine"]["direction"],
            "dateTime": dateTime,
            "countdown": departure["countdown"]
        }
        rows.append(row)
        
    return render_template('departure_table.html', rows=rows)
    