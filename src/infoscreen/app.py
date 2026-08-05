import os
from contextlib import suppress
from pathlib import Path

from flask import Flask, redirect, url_for

from . import config
from .departure import departure_bp


def create_app(test_config=None):

    # frontend/dist gets copied here during the Docker build (see Dockerfile)
    STATIC_DIR = Path(__file__).parent / "static"

    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        config.init_app(app)
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
        return redirect(url_for("departure.departure"))

    @app.route("/healthz")
    def healthz():
        return "ok"

    app.register_blueprint(departure_bp)

    return app
