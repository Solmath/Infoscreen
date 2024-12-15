from flask import Flask, jsonify, render_template
from datetime import datetime
from zoneinfo import ZoneInfo
from EFA_API import EFA

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/departures')
async def departures():
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    # dt = datetime(2020, 10, 31, 12, tzinfo=ZoneInfo("Europe/Berlin"))
    efa = EFA("https://efa.vvs.de/vvs/")
    departures = await efa.get_departures("Stuttgart", "Vaihingen", now)
    return jsonify(departures)

if __name__ == '__main__':
    app.run(debug=True)