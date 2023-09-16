# syntax=docker.io/docker/dockerfile:1.5
ARG PYTHON_VERSION=3.11

FROM docker.io/python:${PYTHON_VERSION}-slim-bookworm as build

WORKDIR /app

# NOTE: we use a special cache mount for the pip cache
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/home/nonroot/.cache,id=pip-cache-poetry-install \
    pip install "poetry==1.4.2"

COPY --chown=nonroot:nonroot pyproject.toml poetry.* ./

# NOTE: add poetry to path
ARG PATH="$PATH:/home/nonroot/.local/bin"
ARG POETRY_NO_INTERACTION=true
ARG POETRY_VIRTUALENVS_OPTIONS_NO_SETUPTOOLS=true
ARG POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true
ARG POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=true

# FIXME: figure out why cache is not working
RUN --mount=type=cache,target=/home/nonroot/.cache,id=poetry-install \
    poetry install --sync --no-root --only main \
    && rm -rf .venv/pyvenv.cfg .venv/src .venv/.gitignore

FROM docker.io/python:${PYTHON_VERSION}-slim-bookworm as base

WORKDIR /app

COPY --chown=nonroot:nonroot --from=build  /app/.venv /app/.venv
COPY --chown=nonroot:nonroot dht_torznab dht_torznab 
COPY --chown=nonroot:nonroot gunicorn.conf.py alembic.ini ./


# TODO: figure out why adding PYTHONPATH is necessary
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/.venv/lib/python3.11/site-packages"

ENTRYPOINT [ "python" ]

FROM base as listener

CMD [ "-m", "dht_torznab.listener" ]

FROM base as peer_count_updater

CMD [ "-m", "dht_torznab.peer_count_updater" ]

FROM base as api

ENTRYPOINT [ "gunicorn" ]

EXPOSE 8080/tcp

FROM base as migrations

ENTRYPOINT [ "alembic" ]
CMD [ "upgrade", "head" ]