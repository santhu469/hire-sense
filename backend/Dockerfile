FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Single image for both the API and the evaluation worker -- which one runs
# is picked at container start via PROCESS_TYPE, so Railway (or any other
# host) needs no per-service Dockerfile/start-command override, just one
# env var set differently on each service.
CMD ["sh", "-c", "if [ \"$PROCESS_TYPE\" = \"worker\" ]; then exec python -m app.workers.evaluation_worker; else exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}; fi"]
