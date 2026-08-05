# Agent Instructions

Self-hosted Flask + Svelte departure board for EFA-based public transport APIs.
Built for kiosk-style displays (e.g. a wall-mounted screen showing next departures
for a configurable set of boards).

## Environment

- **Python**: 3.14, managed with `uv` (not pip/venv directly)
- **Package layout**: `src/` layout, package is `infoscreen`
- **Frontend**: Svelte 5 (runes) + Vite + TypeScript + Tailwind CSS v4, in `frontend/`,
  managed with `npm`
- **Shell**: PowerShell (Windows), zsh (Linux)

## Repository structure

```text
src/infoscreen/
  __init__.py       # empty -- do not put app logic here
  app.py             # Flask app factory (create_app), serves the built Svelte SPA at "/"
  config.py         # env-var loader (init_app) -- fail-fast on missing required vars
  efa_client.py      # EFA transit API client (sync httpx, module-level singleton client)
  departure.py       # blueprint: /departure, /departure_table, /api/* routes
  templates/         # Jinja fallback templates (used when the SPA isn't built)
  static/            # frontend/dist gets copied here during the Docker build
frontend/            # Svelte 5 + Vite + TypeScript SPA
  src/App.svelte      # fetches /api/boards + /api/departures at runtime
tests/               # pytest, respx for HTTP mocking -- never hits a live API
docker-compose.yml   # local dev, reads ./.env (untracked), mounts ./instance -> /app/instance
Dockerfile           # multi-stage build: frontend-builder (node) -> builder (uv) -> final
```

## Commands

- Install backend deps: `uv sync`
- Install frontend deps: `cd frontend && npm ci`
- Run backend tests: `uv run pytest`
- Backend lint/format: `pre-commit run --all-files` (ruff check + format, yaml/toml checks, etc.)
- Frontend format/typecheck/lint: from `frontend/`, `npm run format`, `npm run check`, `npm run lint`
- Run locally (containerized): `cp .env.example .env` (fill in values), `cp boards.example.json instance/boards.json`,
  then `docker compose up -d --build` (or `podman compose up -d --build` -- both are used
  interchangeably against the same `docker-compose.yml`), then visit `http://localhost:8080/`
- Run locally (bare metal): `uv sync`, `cp .env.example .env`, `cp boards.example.json src/instance/boards.json`,
  `uv run flask --app infoscreen.app run --debug`; separately `cd frontend && npm run dev` for the SPA dev server
  (proxies `/api/*` to the Flask dev server on `:5000`)
- Regenerate lockfile after touching dependencies: `uv lock`

## Conventions

- **No hardcoded location data.** All transit-operator/location specifics (EFA URL,
  place, station names, timezone) come from environment variables via `config.py`,
  never from source. This includes test fixtures — use generic placeholders
  (`TestCity`, `Central`, `North`, `example.invalid`), not real operator/station names.
- **Board layout is runtime config, not build-time.** Which boards to show (station,
  line/direction filters, title, count) lives in `boards.json` inside the Flask
  instance folder, read fresh on every `/api/boards` request by `_load_boards_config()`
  in `departure.py` — never imported into the frontend bundle, so it can be edited or
  swapped without a rebuild. Missing/invalid JSON degrades to an empty boards list,
  never a 500. See [boards.example.json](boards.example.json) for the shape.
- `app.py`'s `create_app()` takes an `INSTANCE_PATH` env var to pin the instance
  folder to a fixed, volume-mountable path in Docker; unset locally, Flask falls back
  to its usual auto-detected `src/instance` path. Both `instance/` (repo root, for the
  Docker Compose mount) and `src/instance/` (local dev) are git-ignored.
- `efa_client.py`'s HTTP client is a module-level singleton — keep request payloads
  built fresh per call (no shared mutable state between requests). Response caching
  lives in `departure.py`'s per-station `_cache` dict, not in `efa_client.py`. Tests
  must clear `infoscreen.departure._cache` between runs (see `tests/conftest.py`'s
  autouse fixture).
- Station input from users is validated against the `EFA_STATIONS` allowlist
  (invalid station → 400), and upstream EFA failures are caught (`EFAError`) and
  rendered as a graceful fallback page, never a 500.
- EFA's `departureList` can be present but `null` (not just absent) when a valid
  station has no current departures — always use `data.get("departureList") or []`,
  never `data.get("departureList", [])`.
- `target-version = "py314"` in `pyproject.toml`'s ruff config — PEP 758 syntax
  (unparenthesized `except A, B:`) is valid and intentional in this codebase; don't
  "fix" it to `except (A, B):`.
- The `Dockerfile`'s final stage has its own `CMD` (`waitress-serve ... --call
  infoscreen.app:create_app`); `docker-compose.yml` doesn't override it. Pass an
  equivalent command explicitly when smoke-testing with a bare `docker run`/`podman run`.

## Git workflow

PRs are managed with the [`gh stack`](https://github.com/github/gh-stack) CLI extension
for stacked PRs. Typical flow for a group of related changes:
`gh stack init <branch>` → `gh stack add -Am "<msg>"` per layer → `gh stack submit --auto`
(the `--auto` flag avoids an interactive PR-editor prompt) → after review,
`gh stack merge` → `gh stack sync --prune` → `git checkout main && git pull`.


## Git workflow

PRs are managed with the [`gh stack`](https://github.com/github/gh-stack) CLI extension
for stacked PRs. Typical flow for a group of related changes:
`gh stack init <branch>` → `gh stack add -Am "<msg>"` per layer → `gh stack submit --auto`
(the `--auto` flag avoids an interactive PR-editor prompt) → after review,
`gh stack merge` → `gh stack sync --prune` → `git checkout main && git pull`.
