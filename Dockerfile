####################
# FRONTEND BUILDER #
####################

FROM node:26-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

###########
# BUILDER #
###########

FROM python:3.14.6-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/src ./src
# The Svelte app is bundled as package data, served by Flask at static_url_path="".
COPY --from=frontend-builder /frontend/dist ./src/infoscreen/static
RUN uv sync --frozen --no-dev --no-editable


#########
# FINAL #
#########

FROM python:3.14.6-slim-bookworm

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
# Runtime config (e.g. boards.json) lives here, outside the image -- mount a
# volume at this path to change it without rebuilding.
ENV INSTANCE_PATH=/app/instance

COPY --from=builder /app/.venv ./.venv

RUN chown -R app:app /app
USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

CMD ["waitress-serve", "--listen=0.0.0.0:8080", "--call", "infoscreen.app:create_app"]
