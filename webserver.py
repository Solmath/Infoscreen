from flask import Flask, jsonify, render_template
from datetime import datetime

import EFA

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/departures')
async def departures():
    now = datetime.now()
    efa = EFA.EFA("https://efa.vvs.de/vvs/")
    departures = await efa.get_departures("Stuttgart", "Vaihingen", now)
    return jsonify(departures)

if __name__ == '__main__':
    app.run(debug=True)