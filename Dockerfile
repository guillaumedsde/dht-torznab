FROM python:3.9-buster as build

ARG PIPENV_VENV_IN_PROJECT="enabled"

WORKDIR /opt/app

RUN pip install --no-cache-dir pipenv \
    && pipenv install --dev --deploy

FROM python:3.9-buster-slim

RUN adduser -D app

USER app

COPY --chown=app:app --from=build /opt/app/.venv /opt/app/.venv

COPY . .

ENV PATH="/opt/app/.venv/bin:$PATH"

CMD ["manage.py", "runserver", "8080"]