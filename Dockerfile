FROM docker.io/python:3.11-slim-bullseye AS build

RUN --mount=type=cache,target=/root/.cache \
    pip install "poetry==1.4.2"

WORKDIR /app

COPY poetry* pyproject.toml ./

ARG POETRY_NO_INTERACTION=1
ARG POETRY_VIRTUALENVS_IN_PROJECT=true
ARG POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=true
ARG POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true
ARG POETRY_VIRTUALENVS_OPTIONS_NO_SETUPTOOLS=true

RUN --mount=type=cache,target=/root/.cache \
    poetry install --sync --no-root


FROM docker.io/python:3.11-slim-bullseye

USER 1000

WORKDIR /app

COPY --from=build --chown=1000:1000 /app/.venv /app/.venv
COPY --chown=1000:1000 dht_torznab dht_torznab

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "/app/.venv/bin/python" ]
CMD [ "-m", "dht_torznab.listener" ]