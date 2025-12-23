FROM python:3.12-slim

WORKDIR /app

RUN pip install pdm

COPY pyproject.toml pdm.lock ./
RUN pdm install --prod --no-editable

COPY ./src ./src
COPY ./setup.sh ./setup.sh
COPY ./.env ./.env
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic
