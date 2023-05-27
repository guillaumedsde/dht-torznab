FROM cgr.dev/chainguard/python:3.11-dev as build

WORKDIR /app

# NOTE: we use a special cache mount for the pip cache
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/home/nonroot/.cache \
    pip install "poetry==1.4.2"

COPY --chown=nonroot:nonroot pyproject.toml poetry.* ./

ARG POETRY_NO_INTERACTION=true
ARG PATH="$PATH:/home/nonroot/.local/bin"
ARG POETRY_VIRTUALENVS_OPTIONS_NO_SETUPTOOLS=true
ARG POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true

RUN poetry install --sync --no-root --only main \
    && rm -rf .venv/pyvenv.cfg .venv/src .venv/.gitignore

FROM cgr.dev/chainguard/python:3.11

WORKDIR /app

COPY --from=build --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --chown=nonroot:nonroot dht_torznab dht_torznab
COPY --chown=nonroot:nonroot gunicorn.conf.py gunicorn.conf.py

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "python" ]

CMD [ "-m", "dht_torznab.listener" ]