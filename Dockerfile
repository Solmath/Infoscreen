###########
# BUILDER #
###########

FROM python:3.12.8-slim-bookworm AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# aiohttp ships C extensions that need a compiler to build wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels . waitress

#########
# FINAL #
#########

FROM python:3.12.8-slim-bookworm

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

RUN chown -R app:app $APP_HOME
USER app
