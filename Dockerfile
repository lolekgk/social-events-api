FROM python:3.11.1-slim-buster as requirements-stage

WORKDIR /tmp

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.1-slim-buster as app-stage

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_USER=app_user

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN apt-get update \
  # dependencies for building Python packages, psycopg2
  && apt-get install -y build-essential libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade -r /app/requirements.txt \
  && useradd -rm -d /home/${APP_USER} -s /bin/bash -g root -G sudo -u 1001 ${APP_USER}

COPY . /app/

RUN chmod 111 ./entrypoint.sh

USER ${APP_USER}