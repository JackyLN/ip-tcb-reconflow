# ReconFlow — Intelligent Payment Operations

> **Starter README / target contract.** This repository is not yet an implemented application. Codex must update this README as features are completed; do not claim functionality that does not exist.

ReconFlow is a Python-first, Dockerized **synthetic** banking merchant-settlement reconciliation and AI-assisted exception investigation demonstration for the Techcombank AI Transformation Division Expert Challenge.

## Product

- Import/replay synthetic payment provider, payout and bank-credit records.
- Reconcile one-to-many payment-to-payout data using deterministic rules.
- Explain unusual cases using a bounded, read-only LLM investigator; enforce evidence and confidence gates.
- Require authorized human approval for case resolution; provide full audit history.
- Show measured operations and AI evaluation dashboards and assumption-based financial impact projections.

**Never use actual customer or confidential bank data. No real payments, bank approvals or money movements are implemented.**

## Stack (target)

Python 3.12+, FastAPI, Jinja2, HTMX, Tailwind CSS, Chart.js, PostgreSQL, SQLAlchemy, Alembic, separate Python worker, Docker Compose, Caddy HTTPS.

## Quick start

_Commands to be implemented and verified by Codex:_

```bash
cp .env.example .env
# Set secrets and model provider credentials in .env (optional for offline mode).
docker compose up --build -d
# Run migrations and seed using documented make/compose commands.
```

The app should provide URLs for overview, imports, reconciliation runs, exceptions, investigations, review queue, operations/business/AI reports, audit and controls. The final implemented README must document actual routes, default bind ports and how to access demo roles safely.

## Demo flows

1. Clean scenario — matching payouts and bank credits.
2. Exception scenario — fees, refunds, duplicates, ambiguous candidates, missing/delayed bank credits.
3. Reliability scenario — duplicate import, worker interruption, retry, AI kill switch.

All seeds deterministic, documented and repeatable. Synthetic sample metrics are not actual Techcombank statistics.

## AI

- `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` or equivalent server-side settings.
- Live model invocation requires configured credentials; no-key fallback outputs must be labeled prerecorded.
- Evaluation report must differentiate labeled expected outcomes, actual model results, measured token cost and latency, and failures; do not invent live results.

## Interview deliverables

See [`PLAN.md`](./PLAN.md) for complete coverage and docs: decision memo, discovery, business case, architecture/ADRs, metrics, evaluation, automation, 90-day rollout, and real AI development log.

## Deployment and security

VPS via Docker Compose/Caddy. HTTPS, protected sessions, CSRF, server RBAC, passwords from deployment secrets, no public DB port, persistent volumes, healthchecks, log redaction, backup/restore and rate limits. Finalize and verify exact instructions during implementation.

## Honest status

At handoff: **planning package only**. No application, tested docker images, live model evaluation, stakeholder interviews, business outcomes or deployed URL has been produced in this package.
