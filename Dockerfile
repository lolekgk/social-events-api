FROM python:3.11.1-slim-buster as requirements-stage

WORKDIR /tmp

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.1-slim-buster as app-stage

ENV PYTHONUNBUFFERED 1 \
PYTHONFAULTHANDLER 1 \
PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN apt-get update \
  # dependencies for building Python packages, psycopg2, translations
  && apt-get install -y build-essential libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait

RUN chmod +x /wait

CMD /wait