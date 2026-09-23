# HireSense backend

FastAPI app implementing the Phase 1 core loop (see root `CLAUDE.md` for the
full delivery-phase plan): auth, manual JD create, single resume upload,
async AI evaluation with fixed weights, ranked list, manual status change.

## Setup

```bash
# one-time
uv sync
cp .env.example .env   # edit OPENAI_API_KEY at minimum

# local infra: Postgres (port 5433 -- 5432 is often taken by a native
# install) + LocalStack (S3 + SQS), with the dev bucket/queue auto-created
docker compose up -d

# schema
uv run alembic upgrade head
```

## Run

```bash
# API
uv run uvicorn app.main:app --reload

# Evaluation worker (separate process -- consumes SQS, parses + scores
# candidates). Needs a real OPENAI_API_KEY to complete a job.
uv run python -m app.workers.evaluation_worker
```

API docs at `http://localhost:8000/docs` once the server is running.

## Test

```bash
uv run pytest
```

Tests run against a dedicated `<db>_test` database on the same Postgres
server (created and dropped automatically by `tests/conftest.py`) — they
never touch dev data. They mock the OpenAI client, so no API key is needed
to run the suite.

## Architecture notes

- **`Candidate.processing_status` vs `Candidate.current_status`** — two
  separate columns on purpose. `processing_status` is system-driven
  (pending/parsing/evaluating/completed/failed) and is the only field
  `evaluation_service`/the worker may write. `current_status` (the hiring
  decision) is written **only** by `decision_service`, always from an
  authenticated, human-initiated API call. See CLAUDE.md's non-negotiable
  product rules.
- **Overall score is computed in Python**, not by the LLM —
  `evaluation_service.process_candidate` multiplies each category score by
  its `EvaluationCriteria` weight and sums. The OpenAI structured-output
  call only ever returns per-category scores + insights.
- **Async from day one** — resume upload enqueues an SQS job; the worker
  (`app/workers/evaluation_worker.py`) is a separate long-running process,
  matching the AWS deployment topology (its own ECS Fargate service).
