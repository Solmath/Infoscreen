# Agent Instructions

Self-hosted Flask departure board for EFA-based public transport APIs. Built for
kiosk-style displays (e.g. a wall-mounted screen showing next departures).

## Environment

- **Python**: 3.14, managed with `uv` (not pip/venv directly)
- **Package layout**: `src/` layout, package is `infoscreen`
- **Shell**: zsh

## Repository structure

```text
src/infoscreen/
  __init__.py       # Flask app factory (create_app)
  config.py         # env-var loader (init_app) — fail-fast on missing required vars
  efa.py            # EFA transit API client (sync httpx, module-level TTL cache)
  departure.py       # blueprint: /departure, /departure_table routes
  templates/
  static/
tests/               # pytest, respx for HTTP mocking — never hits a live API
docker-compose.yml   # local dev, reads ./.env (untracked)
Dockerfile           # multi-stage uv build; NO CMD (compose supplies the run command)
```

## Commands

- Install deps: `uv sync`
- Run tests: `uv run pytest`
- Lint/format: `pre-commit run --all-files` (ruff check + format, yaml/toml checks, etc.)
- Run locally: `cp .env.example .env` (fill in values), then `docker compose up -d --build`, then visit `http://localhost:8080/`
- Regenerate lockfile after touching dependencies: `uv lock`

## Conventions

- **No hardcoded location data.** All transit-operator/location specifics (EFA URL,
  place, station names, timezone) come from environment variables via `config.py`,
  never from source. This includes test fixtures — use generic placeholders
  (`TestCity`, `Central`, `North`, `example.invalid`), not real operator/station names.
- `efa_client.py`'s HTTP client is a module-level singleton — keep request payloads
  built fresh per call (no shared mutable state between requests). Response caching
  lives in `departure.py`'s per-station `_cache` dict, not in `efa_client.py`. Tests
  must clear `infoscreen.departure._cache` between runs (see `tests/conftest.py`'s
  autouse fixture).
- Station input from users is validated against the `EFA_STATIONS` allowlist
  (invalid station → 400), and upstream EFA failures are caught (`EFAError`) and
  rendered as a graceful fallback page, never a 500.
- The `Dockerfile` has no `CMD`; the actual serve command lives in `docker-compose.yml`
  (`waitress-serve ... --call "infoscreen:create_app"`). Pass an equivalent command
  explicitly when smoke-testing with a bare `docker run`.

## Git workflow

PRs are managed with the [`gh stack`](https://github.com/github/gh-stack) CLI extension
for stacked PRs. Typical flow for a group of related changes:
`gh stack init <branch>` → `gh stack add -Am "<msg>"` per layer → `gh stack submit --auto`
(the `--auto` flag avoids an interactive PR-editor prompt) → after review,
`gh stack merge` → `gh stack sync --prune` → `git checkout main && git pull`.
