import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, jsonify, request, session, url_for
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
    # return jsonify(departures)

    return render_template('departure_table.html')