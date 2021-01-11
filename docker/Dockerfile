ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION}-buster as build

WORKDIR /opt/app

RUN pip install --no-cache-dir pipenv==2020.11.15

COPY Pipfile* ./

FROM build as dev

RUN pipenv install --dev --deploy --system

WORKDIR /opt/app

COPY --chown=1000:1000 . .

RUN chmod 755 /opt/app/docker/entrypoint.sh /opt/app/listener.py

USER 1000

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/opt/app/docker/entrypoint.sh" ]

FROM build as build-prod

ARG PIPENV_VENV_IN_PROJECT="enabled"

RUN pipenv install --deploy

FROM python:${PYTHON_VERSION}-slim-buster as prod

WORKDIR /opt/app

COPY --chown=1000:1000 --from=build-prod /opt/app/.venv /opt/app/.venv

COPY --chown=1000:1000 ./*.py ./

COPY --chown=1000:1000 torznab torznab

COPY --chown=1000:1000 api api

USER 1000

ENV PATH="/opt/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

FROM prod as api

ENTRYPOINT ["/opt/app/.venv/bin/uvicorn", "torznab.asgi:application", "--host", "0.0.0.0", "--port", "8080"]

FROM prod as listener

ENTRYPOINT ["/opt/app/.venv/bin/python", "./listener.py"]
