FROM cgr.dev/chainguard/python:3.10-dev as build

WORKDIR /app

# NOTE: we use a special cache mount for the pip cache
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/home/nonroot/.cache \
    pip install "poetry==1.4.2"

COPY pyproject.toml poetry.lock ./

ARG POETRY_NO_INTERACTION=true
ARG POETRY_VIRTUALENVS_CREATE=false

RUN --mount=type=cache,target=/home/nonroot/.cache \
    poetry install --sync --no-root --only main

FROM cgr.dev/chainguard/python:3.10

WORKDIR /app

COPY --from=build --chown=nonroot:nonroot /home/nonroot/.local/lib/python3.11/site-packages /home/nonroot/.local/lib/python3.11/site-packages
COPY --chown=nonroot:nonroot dht_torznab dht_torznab
COPY --chown=nonroot:nonroot gunicorn.conf.py gunicorn.conf.py

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python" ]

CMD [ "-m", "dht_torznab.listener" ]