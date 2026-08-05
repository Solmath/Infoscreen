# Infoscreen

A self-hosted departure board for EFA-based public transport APIs. Built with Flask,
served with waitress, designed for kiosk-style displays (e.g. a wall-mounted screen
showing upcoming departures for a set of stations).

## Features

- Fetches real-time departure data from an EFA (Elektronische Fahrplanauskunft) endpoint.
- Displays line, destination, departure time, countdown, and delay.
- Station list, transit operator endpoint, and timezone are fully configured via
  environment variables — no location data is baked into the code.
- Short-lived caching and graceful degradation: if the upstream EFA endpoint is
  slow or unavailable, the app shows a fallback message instead of erroring out.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker (optional, for containerized runs)

## Configuration

All configuration is via environment variables (see [.env.example](.env.example)):

| Variable        | Required | Description                                                |
|-----------------|----------|--------------------------------------------------------------|
| `EFA_URL`       | yes      | Base URL of your transit operator's EFA endpoint            |
| `EFA_PLACE`     | yes      | Default place/city name passed to the EFA API                |
| `EFA_STATIONS`  | yes      | Comma-separated list of selectable station names              |
| `EFA_TIMEZONE`  | no       | Timezone for displayed times (default: `UTC`)                 |
| `EFA_TIMEOUT`   | no       | HTTP timeout in seconds for EFA requests (default: `5.0`)     |
| `EFA_CACHE_TTL` | no       | Seconds to cache EFA responses (default: `30.0`)              |

The app fails fast at startup if a required variable is missing.

### Board layout

Which boards to show (station, line/direction filters, title) is read at runtime from
a `boards.json` file in the Flask [instance folder](https://flask.palletsprojects.com/en/stable/config/#instance-folders),
not baked into the image -- see [boards.example.json](boards.example.json) for the format.

- Local (no Docker): copy it to `src/instance/boards.json`.
- Docker: copy it to `./instance/boards.json`; `docker-compose.yml` mounts that folder
  read-only into the container (`INSTANCE_PATH=/app/instance`).

The file is re-read on every request, so it can be edited without restarting the app.
If it's missing or invalid, boards.json simply returns no boards.

## Installation (local, without Docker)

```bash
git clone https://github.com/Solmath/Infoscreen.git
cd Infoscreen
uv sync
cp .env.example .env   # git-ignored; fill in your EFA_URL / EFA_PLACE / EFA_STATIONS
cp boards.example.json src/instance/boards.json   # git-ignored; list your boards
set -a; source .env; set +a
uv run flask --app infoscreen.app run --debug
```

## Docker

Pre-built images are published to
[ghcr.io/solmath/infoscreen](https://github.com/Solmath/Infoscreen/pkgs/container/infoscreen)
on every push to `main` (tagged `latest`) and on version tags (tagged with the semver).

```bash
docker run -d -p 8080:8080 --env-file .env ghcr.io/solmath/infoscreen:latest
```

Or build locally with Compose:

```bash
docker compose up -d --build   # start / rebuild after changes
docker compose down            # stop
```

`docker-compose.yml` reads a git-ignored `.env` file. Run `cp .env.example .env`
and fill it in with your real transit operator's values first. Also copy
`boards.example.json` to `./instance/boards.json` to define your boards (see
[Board layout](#board-layout)).

Then open `http://localhost:8080/` in a browser — it redirects to the departure board.
The container exposes a `/healthz` liveness endpoint used by its Docker `HEALTHCHECK`.

## Testing

```bash
uv run pytest
pre-commit run --all-files
```

Tests use [respx](https://lundberg.github.io/respx/) to mock the EFA API and never
make real network calls.

## Project Structure

```text
src/infoscreen/
  __init__.py             # Flask app factory
  config.py                # environment-variable configuration loader
  efa.py                    # EFA API client (sync httpx, TTL cache, error handling)
  departure.py              # routes: /departure, /departure_table
  templates/                # Jinja templates
  static/styles/style.css   # styling
tests/                      # pytest test suite
Dockerfile                  # multi-stage build (uv-based)
docker-compose.yml          # local dev/run configuration
```

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [httpx](https://www.python-httpx.org/)
- [EFA API](https://www.efa.de/)
- EFA class based on https://finalrewind.org/interblag/entry/efa-json-api/
