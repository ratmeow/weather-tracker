FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV  PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry>=1.6.1 \
    && poetry config virtualenvs.create false \
    && poetry config installer.parallel false

WORKDIR /application
COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

COPY weather_tracker weather_tracker
COPY alembic alembic
COPY alembic.ini ./

CMD ["sh", "-c", "alembic upgrade head && uvicorn weather_tracker.app:create_production_app --host 0.0.0.0 --port 8080"]