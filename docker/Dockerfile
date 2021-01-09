FROM python:3.9-buster as build

ARG PIPENV_VENV_IN_PROJECT="enabled"

WORKDIR /opt/app


RUN pip install --no-cache-dir pipenv==2020.11.15

COPY Pipfile* ./

RUN pipenv install --dev --deploy

FROM python:3.9-slim-buster

USER 1000

WORKDIR /opt/app

COPY --chown=1000:1000 --from=build /opt/app/.venv /opt/venv

COPY --chown=1000:1000 . .

RUN chmod 755 /opt/app/docker/entrypoint.sh /opt/app/listener.py

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

ENTRYPOINT [ "/opt/app/docker/entrypoint.sh" ]