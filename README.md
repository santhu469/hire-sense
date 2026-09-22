# HireSense

AI-powered candidate evaluation platform — reduces resume-screening effort with
explainable AI scoring, while keeping the final hiring decision with a human
recruiter or hiring manager.

This repository currently holds the **pre-implementation documentation**
deliverables only (no application code yet):

- [`docs/solution-document/HireSense-Solution-Document.docx`](docs/solution-document/HireSense-Solution-Document.docx)
  — the full solution document: business context, requirements traceability,
  component design, data model, AWS deployment architecture, tech stack, and
  phased delivery roadmap.
- [`docs/architecture/diagrams/`](docs/architecture/diagrams/) — the diagrams
  referenced by the solution document:
  - `system_architecture.png` — logical component architecture
  - `aws_deployment.png` — AWS deployment topology
  - `process_flow.png` — primary application flow (with the two
    human-in-the-loop gates)
  - `data_model_er.png` — core entity-relationship model

## Regenerating the docs

Both the `.docx` and the diagrams are generated from Python scripts so they
stay easy to update and diff. To regenerate them:

```bash
# one-time setup
brew install graphviz
python3 -m venv docs/.venv
docs/.venv/bin/pip install python-docx diagrams

# regenerate diagrams
docs/.venv/bin/python docs/architecture/scripts/system_architecture.py
docs/.venv/bin/python docs/architecture/scripts/aws_deployment.py
docs/.venv/bin/python docs/architecture/scripts/process_flow.py
docs/.venv/bin/python docs/architecture/scripts/data_model_er.py

# regenerate the solution document (embeds the diagrams above)
docs/.venv/bin/python docs/solution-document/generate_solution_doc.py
```

Edit the Python source under `docs/architecture/scripts/` or
`docs/solution-document/generate_solution_doc.py` — not the generated
`.docx`/`.png` files directly — and re-run the relevant script.

## Locked stack decisions (v1)

- Single organization (no multi-tenancy)
- Auth: email/password
- Frontend: Next.js (TypeScript)
- Backend: Python (FastAPI)
- Deployment: AWS (ECS Fargate, RDS PostgreSQL, S3, SQS, SES)

See the solution document's "Open Questions & Assumptions" section for what's
still unconfirmed before Phase 1 implementation begins.
