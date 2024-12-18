from flask.cli import FlaskGroup

from infoscreen import app


cli = FlaskGroup(app)


def create_app():
    return app


if __name__ == "__main__":
    cli()
