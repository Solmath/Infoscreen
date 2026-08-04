###########
# BUILDER #
###########

FROM python:3.12.8-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

#########
# FINAL #
#########

FROM python:3.12.8-slim-bookworm

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv ./.venv

RUN chown -R app:app /app
USER app
