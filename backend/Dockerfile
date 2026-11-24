FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY --chown=app:app backend/app ./app

RUN poetry install --only main --no-root



# ------- Финальный образ -------
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 \
    --no-create-home --shell /usr/sbin/nologin app 

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder --chown=app:app /app/app ./app

USER app

EXPOSE 8000

CMD ["python", "app/main.py"]
