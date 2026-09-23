# HireSense

AI-powered candidate evaluation platform. Full context lives in
[`docs/solution-document/HireSense-Solution-Document.docx`](docs/solution-document/HireSense-Solution-Document.docx)
and the diagrams under [`docs/architecture/diagrams/`](docs/architecture/diagrams/) —
read those before making architectural changes, and update them (regenerate
via their source scripts) if an implementation decision diverges from what
they describe.

## Non-negotiable product rules

These come directly from the client's requirements and constrain how code
in this repo may be written — do not implement a shortcut around them:

- **AI never finalizes a hiring decision.** Candidate status
  (Shortlisted/Hold/Rejected) can only change through a human-initiated,
  authenticated API call. No evaluation/scoring job may write to status.
- **Outbound email always requires an explicit human send action.** The AI
  may draft email content, but sending is a separate, logged action gated
  on human approval — never automatic.
- **Every score ships with a reason.** Evaluation output is never a bare
  number — always accompanied by structured insights (strengths, gaps,
  recommendation).
- **Scores and decisions are versioned/append-only, not overwritten** —
  rescoring inserts a new `Evaluation` row (`is_latest` flag); status
  changes insert a new `CandidateDecision` row. This is how audit history
  is preserved.
- **Evaluation weights are configurable per JD**, not hardcoded into a
  prompt — they live in the `EvaluationCriteria` table.

## Locked stack decisions (v1)

- Single organization (no multi-tenancy)
- Auth: email/password (JWT access/refresh) — no SSO in v1
- Frontend: Next.js (TypeScript)
- Backend: Python, FastAPI, SQLAlchemy + Alembic
- Database: PostgreSQL
- Object storage: S3 (resumes)
- Async jobs: SQS + a dedicated worker service
- LLM: OpenAI API (structured outputs / function calling — never parse free text for scores)
- Email: AWS SES
- Deployment: AWS ECS Fargate (frontend, backend API, worker — 3 services), see
  `docs/architecture/diagrams/aws_deployment.png`

## Planned repo structure

```
hire-sense/
├── frontend/          # Next.js app
├── backend/           # FastAPI app (routers/, services/, models/, workers/)
├── infra/             # IaC (future — not yet started)
├── docs/              # solution document + architecture diagrams (see above)
└── CLAUDE.md
```

`backend/` and `frontend/` are both scaffolded for Phase 1 core loop: auth,
JD CRUD, async single-resume ingestion + evaluation, ranking, manual
decision — see `backend/README.md` and `frontend/README.md` for full setup.

## Commands

- Frontend dev server: `cd frontend && npm run dev` (needs Node ≥20 -- see `frontend/README.md` if `node -v` is older)
- Frontend build/lint: `cd frontend && npm run build` / `npm run lint`
- Backend local infra (Postgres + LocalStack S3/SQS): `cd backend && docker compose up -d`
- Backend dev server: `cd backend && uv run uvicorn app.main:app --reload`
- Backend worker: `cd backend && uv run python -m app.workers.evaluation_worker`
- Backend tests: `cd backend && uv run pytest`
- Backend migrations: `cd backend && uv run alembic upgrade head` (new migration: `uv run alembic revision --autogenerate -m "..."`)

## Delivery phases

Building in this order (see solution document Section 13 for full detail) —
don't jump ahead to RBAC/rescoring/communication polish before the core loop
works end-to-end:

1. Core loop (MVP): auth, manual JD create, single resume upload, AI
   evaluation with fixed weights, ranked list, manual status change.
2. Scale ingestion: bulk upload, async job queue, 100+ resumes/JD.
3. Configurable weights + versioned rescoring + decision audit trail.
4. Full RBAC (Admin / Recruiter / Viewer).
5. Communication (AI draft → human approval → send).
6. AI JD generation/improvement, candidate ranking-rationale polish.

## Secrets

Never commit API keys, DB credentials, or JWT signing secrets. Local dev
uses a gitignored `.env`; production uses AWS Secrets Manager (see solution
document Section 10.1). If you ever see a real secret in a diff, stop and
flag it rather than committing it.
