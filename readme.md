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

## Installation (local, without Docker)

```bash
git clone https://github.com/Solmath/Infoscreen.git
cd Infoscreen
uv sync
cp .env.example .env   # git-ignored; fill in your EFA_URL / EFA_PLACE / EFA_STATIONS
set -a; source .env; set +a
uv run flask --app infoscreen run --debug
```

## Docker

```bash
docker compose up -d --build   # start / rebuild after changes
docker compose down            # stop
```

`docker-compose.yml` reads a git-ignored `.env` file. Run `cp .env.example .env`
and fill it in with your real transit operator's values first.

Then open `http://localhost:8080/` in a browser — it redirects to the departure board.

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
