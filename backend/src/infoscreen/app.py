import os
from contextlib import suppress
from pathlib import Path

from flask import Flask, redirect, send_from_directory, url_for

from . import config
from .departure import departure_bp

# frontend/dist gets copied here during the Docker build (see Dockerfile)
STATIC_DIR = Path(__file__).parent / "static"


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        # Lets Docker pin the instance folder to a fixed, mountable path;
        # unset locally, so Flask falls back to its usual auto-detected path.
        instance_path=os.environ.get("INSTANCE_PATH") or None,
        static_folder=str(STATIC_DIR),
        static_url_path="",
    )

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
        if (STATIC_DIR / "index.html").is_file():
            return send_from_directory(STATIC_DIR, "index.html")
        # Frontend not built (e.g. plain `flask run` in local dev) -- fall back
        # to the server-rendered board.
        return redirect(url_for("departure.departure"))

    @app.route("/healthz")
    def healthz():
        return "ok"

    app.register_blueprint(departure_bp)

    return app
