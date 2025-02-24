import os

from flask import Flask, jsonify, render_template
from datetime import datetime
from zoneinfo import ZoneInfo
from EFA_API import EFA
from contextlib import suppress


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    with suppress(OSError):
        os.makedirs(app.instance_path)

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/json")
    async def get_json():
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        efa = EFA("https://efa.vvs.de/vvs/")
        departures = await efa.get_departures("Stuttgart", "Vaihingen", now)
        return jsonify(departures)

    from . import departure, cambridge

    app.register_blueprint(departure.bp)
    app.register_blueprint(cambridge.bp)

    return app
