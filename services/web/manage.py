from flask.cli import FlaskGroup

import infoscreen

app = infoscreen.create_app()
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
