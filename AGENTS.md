# Codex Agent Instructions — ReconFlow

Read `PLAN.md` before making changes. The target is an interview-grade, deployable, **Python-first banking operations application**. `PLAN.md` is the single source of truth for scope, acceptance criteria, design decisions and challenge traceability.

## Operating method
1. Inspect repository and existing state before edits; never blindly overwrite user work.
2. At the start of each phase summarize intended files, dependencies and acceptance checks; then IMPLEMENT, TEST and UPDATE `PLAN.md` progress markers/checklist, `README.md` and `docs/ai-log.md` with truthful observations.
3. Work in small vertical slices; prioritize working paths over architectural ceremony. Do not replace functioning features with UI mockups.
4. Verify each phase with automated tests and Docker smoke checks where available; report exact commands, successes, failures and omissions. Do not claim tests were run if they were not.
5. Make safe implementation choices without needless questions. Ask only when blocked by secret credentials or irreconcilable product constraints. Never require a paid model API to run baseline tests.
6. Never invent stakeholder interviews, real bank metrics, ROI facts, live LLM evaluation numbers, or production security assurance. Label synthetic test data, scenario values and financial projections clearly.
7. If time is tight, implement the complete end-to-end path first; record deferred enhancements explicitly.

## Technical guardrails
- Python 3.12+, FastAPI, PostgreSQL, Alembic, SQLAlchemy, Jinja2/HTMX, local static assets, one worker process. Docker Compose VPS-targeted. No mandatory Redis, Kafka, Kubernetes, n8n or frontend SPA.
- Prefer clean modular services and explicit dependency boundaries. Avoid circular imports and business logic in route handlers/templates.
- Always use integer minor units for money with currency-specific exponent (VND 0, USD 2), no float arithmetic. Never pretend individual payments directly map 1:1 to bank credits when payout batching is involved.
- Reconciliation, ledger-type math and policy gates are deterministic. LLM can only propose explanations/next steps with evidence, never move money, write finance records, approve transactions or execute arbitrary SQL/HTTP.
- Enforce RBAC on server routes/actions. Maker-checker: proposer cannot approve own resolution; auditor cannot mutate; only admin may toggle controls. Protect forms from CSRF, sessions appropriately, APIs with authorization.
- Durable DB jobs, unique/idempotency constraints, retry/backoff, failure injection and audit logging required. Replaying an import must not double count.
- Validate all AI outputs with schema, evidence ID membership and server-side policy. Bound tool calls/time/tokens and record token usage + estimated provider cost. Offline mode must say it is prerecorded/simulated, never masquerade as live AI.
- Protect PII/secrets in logs and exports, keep `.env` out of VCS. The deployed demo can accept uploads of synthetic/public data only.
- UI must be high quality: polished layout, clear empty/loading/error states, accessible status colors, mobile-friendly overview and desktop data tables, consistent design tokens, sample scenario picker, no placeholder buttons.

## Required code quality
- Use type hints, docstrings at boundaries, Ruff formatting/linting, pytest unit and API tests, migrations, seed reproducibility with fixed RNG.
- Tests: currency and fee calculations; payout aggregation; ambiguity cases; duplicate import/re-run; job recovery; permissions/maker-checker; AI schema/evidence rejection; kill switch; main UI routes.
- CLI/Make targets: `up`, `down`, `migrate`, `seed`, `test`, `lint`, `eval`, `smoke` (or document equivalent exact commands).
- No production mutation in seed/reset by default; `DEMO_MODE` gating and double-confirm guard for dangerous reset.
- Ensure `docker compose up --build -d` + migration/seed procedure works on a clean VPS; compose services healthcheck; volumes; HTTPS instructions.

## Documentation contract
- `README.md`: setup, demo logins (without hardcoded shared passwords), scenarios, model configuration, no-key fallback, tests, deployment, known gaps.
- `PLAN.md`: milestone progress, traceability and decisions. Update when implementation differs.
- `docs/decision-memo.md`, `docs/discovery.md`, `docs/business-case.md`, `docs/architecture.md`, `docs/metrics.md`, `docs/rollout.md`, `docs/evaluation.md`, `docs/ai-log.md`, `docs/demo-script.md`, `docs/adoption.md`, ADRs.
- AI log needs 5–10 *actual* important prompts, failures/corrections and reflection; never fabricate logs.
- Mark what is MEASURED, ASSUMED, SIMULATED, PROPOSED and NOT IMPLEMENTED everywhere it affects interpretation.

## Final self-review
Report: (1) real implemented flows (2) test commands/results (3) screens/routes (4) AI provider mode and evaluation findings (5) security limitations (6) live demo/deploy steps (7) challenge requirements not fully met (8) recommended live-change demonstration.
