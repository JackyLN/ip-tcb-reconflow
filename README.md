# ReconFlow · Merchant settlement operations

Working Python-first **synthetic** banking operations prototype: CSV evidence → payment aggregation
into provider payouts → bank-credit reconciliation → exception investigation → human proposal →
independent supervisor decision → audit. No real customer data, bank integration or money movement.
The workflow is a product hypothesis, not a claim about Techcombank's internal systems.

## Run locally

Requirements: Docker with Compose, Python 3 for secret setup. `uv` is needed for local tests/smoke;
Node is needed only to rebuild local assets or run browser checks. Docker builds assets itself.

```sh
make configure                  # creates private .env; preserves an existing file
# Fresh install: create database, migrate and seed before starting application traffic.
docker compose build
docker compose up -d db
make migrate
mkdir -p artifacts
(umask 077; make seed > artifacts/demo-credentials.txt)
docker compose up -d --wait
```

Open **http://localhost:8080**. Read local credentials from `artifacts/demo-credentials.txt` privately.
Accounts: `analyst@reconflow.demo`, `supervisor@reconflow.demo`, `manager@reconflow.demo`,
`auditor@reconflow.demo`, `admin@reconflow.demo`. Each has an independently generated password,
printed only when first created. No fixed/shared password is published. `.env` and artifacts are
ignored by Git and excluded from Docker builds. Seed preserves existing data/accounts/passwords;
keep first-seed output safe, since it cannot recover existing passwords.

`make up` runs `docker compose up --build -d`. `make down` stops services and preserves volumes.
Local demo uses HTTP/COOKIE_SECURE=false. Public deployments require HTTPS/secure cookies; see
[deployment instructions](docs/deployment.md). App/worker run nonroot with read-only filesystems;
PostgreSQL has persistent storage and no public port. All four services have healthchecks.

## What works

- Fixed-RNG synthetic clean/mismatch/failure scenarios at 100, 1,000 and 10,000 payments, 20 per
  payout. Refunds, fee mismatches, missing/wrong/late/currency credits and duplicate candidates.
- Atomic validated UTF-8 CSV imports, source SHA-256/provenance, unique source IDs, safe CSV export.
  Download `/imports/template.csv` and intended labels at `/scenarios/labels.csv`. Amounts are integer minor units: VND 0 decimals, USD 2.
- Per-payout half-up fees and net math, strict reference/account/currency/time matching. Ambiguous
  references stay unresolved. No false individual-payment-to-credit matching or cross-currency netting.
- PostgreSQL-leased durable jobs, atomic DB effects, restart/lease recovery, exponential retry,
  failure injection, three-attempt dead letter, worker heartbeat and in-app alerts.
- Server-side sessions, Argon2 hashes, CSRF, server role gates, analyst/supervisor proposals,
  supervisor decisions with maker != checker, admin-only controls, auditor read-only domain access.
- Four read-only AI tools, validated report/citation membership, human review policy, daily quotas,
  kill switch, invocation accounting, explicit no-key SIMULATED advisory output and live-failure fallback.
- Database-calculated snapshot KPIs, Chart.js distribution, editable annual USD capacity sensitivity,
  audit chain and PostgreSQL append-only UPDATE/DELETE guard. No finance writes from AI or approvals.

Roles share one synthetic workspace. Admin may import/launch scenarios and manage controls/profiles;
analyst imports/investigates/proposes; supervisor investigates/proposes/reviews others' proposals;
manager/auditor read. All roles sign in/out. See [security boundary](docs/security.md).

## Screens and demo

| Route | Purpose |
| --- | --- |
| `/`, `/login` | Measured overview and authentication |
| `/imports`, `/imports/{id}` | Scenario launcher, CSV import, provenance, replay/export |
| `/runs`, `/runs/{id}` | Durable reconciliation runs and findings |
| `/payouts`, `/payouts/{id}` | Paginated payout list, payment/refund/net and bank evidence |
| `/exceptions`, `/exceptions/{id}` | Worklist, cited evidence, bounded AI, human proposal/history |
| `/investigations`, `/review` | Advisory results and independent decisions |
| `/reports/operations`, `/reports/impact` | Measured snapshot versus assumed business value |
| `/ai/evaluation`, `/audit` | Reproducible eval results, provider accounting, audit history |
| `/operations/health`, `/controls`, `/guide` | Worker alerts, kill switch, provider profiles, architecture/rollout |
| `/healthz`, `/readyz` | DB connectivity and seeded readiness |

Follow [demo script](docs/demo-script.md): analyst launches 1,000-payment mismatch; inspect a payout;
queue AI and refresh; submit a human recommendation; sign out/in as supervisor and review; inspect
audit; replay import; launch failure scenario; admin toggles AI; inspect evaluation/business assumptions.
Refresh links show current persistent worker state; no placeholder CTAs. Main views are bounded
(100–500 records); payout list has 50-row pagination. Full-worklist pagination is deferred.

Recommended live change: add a second versioned provider policy and import new synthetic IDs, or
change a fee example and run `uv run pytest tests/test_domain.py -k fee -q`. Explain deterministic
payout rounding and why historical policies are preserved.

## AI configuration and evaluation

Chosen demo model: **GPT-5.4 mini**, pinned to `gpt-5.4-mini-2026-03-17`.
[ADR 004](docs/adr/004-demo-llm-selection.md) records the rationale, dated pricing assumptions
(USD 0.75 input / 4.50 output per million tokens), and target environment values. **Adapter changes
and live evaluation are pending:** replace `max_tokens` with `max_completion_tokens` and explicitly
set request `reasoning_effort` to `none` initially before enabling this target. The decision does
not claim measured model quality, latency or live compatibility.

Baseline runs with **no key**. SIMULATED results are scripted, low-confidence, advisory only.
No live model accuracy, live cost or provider compatibility is claimed for the no-key demonstration.
To enable the configured OpenAI-compatible HTTP adapter, set private `.env` values:

```dotenv
LLM_BASE_URL=https://your-trusted-provider.example/v1
LLM_MODEL=your-model
LLM_API_KEY=your-private-key
LLM_INPUT_USD_PER_MILLION=0
LLM_OUTPUT_USD_PER_MILLION=0
```

Use verified provider prices; zero means **unpriced**, not free. Recreate app/worker after changes:
`docker compose up -d --force-recreate app worker`. Clicking investigate then explicitly queues
live inference. AI has four tool calls, at most five HTTP calls, 1,200 completion tokens per call,
HTTP timeouts and daily job caps (20/user, 100/global). Reports never create proposals or resolve cases.

```sh
make eval                         # offline contract validation, never paid
# Optional paid holdout inference, only when explicitly chosen:
docker compose run --rm app python -m reconflow.cli eval --live --limit 6
```

Export generator CSV/ground truth independently:
`docker compose run --rm app python -m reconflow.cli dataset --count 1000 --scenario mismatch`;
add `--labels` for intended labels. These labels are synthetic expectations, not observed AI results.

72 labeled synthetic cases: 24 development and 48 holdout, including ambiguous/contradictory/missing
and adversarial evidence. Offline checking reports schema/citation validity and deterministic baseline;
it does not pass expected labels off as model predictions. Live evaluation records failures, confusion,
latency and actual token usage with configured cost estimates. Semantic hallucination and confidence
calibration require human grading and are **NOT MEASURED**. [Evaluation detail](docs/evaluation.md).

## Verification

```sh
uv sync --python 3.12 --frozen
make lint test
npm ci --ignore-scripts
npm run check
npm run build
make smoke                       # requires first-seed private credentials file and running stack
make eval
docker compose exec -T app python -m scripts.postgres_checks
docker compose run --rm app python -m scripts.benchmark
npx playwright install chromium
npm run browser                  # desktop/mobile screenshots under ignored artifacts/
```

MEASURED on 2026-11-06: 28 pytest unit/API/mocked-provider tests passed without keys; Ruff passed.
A dependency emits one Starlette TestClient/httpx deprecation warning. PostgreSQL migration/seed,
Docker HTTP end-to-end smoke, offline 48/48 schema/evidence checks, competing job-claim check,
audit hash-chain verification and audit UPDATE guard passed. Browser verification is recorded in
[verification log](docs/verification.md), including corrections and exact final outcomes.
GitHub Actions lint/tests and Docker workflow passed for the deployed source:
[verified CI run](https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42415477106).
Manual CD awaits the user-managed deployment secrets.

[Benchmark artifact](docs/benchmark.json) contains actual isolated synthetic measurements and
instance limits; these measure application processing, not human labor savings or bank throughput.

## Documentation and honest gaps

[PLAN.md](PLAN.md) tracks scope, checkboxes and decisions. Supporting artifacts:
[discovery](docs/discovery.md), [decision memo](docs/decision-memo.md),
[business case](docs/business-case.md), [architecture](docs/architecture.md),
[metrics](docs/metrics.md), [rollout](docs/rollout.md), [adoption](docs/adoption.md),
[AI development log](docs/ai-log.md), [ADRs](docs/adr/), [deployment](docs/deployment.md).

Not complete: five stakeholder interviews (A1 not met), live provider evaluation, demo video,
measured human baseline/A-B pilot, full within-SLA north star/period reporting,
semantic hallucination grading, calibrated confidence, ramp/rework monthly ROI, external alerts,
restore drill, separate refund ledgers, partial/many-to-many settlement, bank connectors/SSO/MFA,
tenant isolation, separate least-privilege DB roles and externally anchored audit retention.
The DB owner can disable audit guards. This is not production-certified banking software.

All sources are SYNTHETIC; UI KPIs/benchmarks are MEASURED only from this prototype; business inputs
are ASSUMED; offline AI is SIMULATED; rollout targets are PROPOSED. Remaining work is explicitly
NOT IMPLEMENTED/VERIFIED. No destructive reset runs by default. The optional operator-only reset
requires DEMO_MODE plus two confirmation flags; see deployment docs.

## UI palette

The console now follows the requested Techcombank-inspired red, black, white and sky-grey palette,
with restrained gold on the measured-data badge and environment label. Exact `#ED1C24` is used for
brand/chart accents; deeper reds provide readable white-text buttons and links. ReconFlow retains
its own name and synthetic-demo identity. Gold is a selected UI accent, not a verified official hex.
See [palette/reference and contrast notes](docs/ui-branding.md).

UI palette verification: `make test` (28 passed, one existing dependency deprecation warning),
`make lint`, `npm run check`, `npm run build`, `npm run browser`, `make smoke` and
`docker compose up --build -d --wait` passed. Screenshots were visually checked at desktop/mobile
sizes; no page/CSP errors or mobile overflow were observed. All four services are healthy.

## Shared VPS / GitHub CD

Live synthetic demo: **https://tcb.jackylenghia.com** (`187.127.220.131`), verified 2026-11-08. The shared VPS
uses its existing Stayflow Caddy proxy; ReconFlow publishes no host ports and keeps a separate
PostgreSQL volume. See [shared VPS deployment and recovery](docs/deployment-shared-vps.md).

`.github/workflows/cd.yml` provides manual **CD** from verified main, with backups, migrations,
preserve-only seeding and public HTTPS checks. User-managed secrets: `VPS_HOST`, `VPS_USER`,
`VPS_SSH_PRIVATE_KEY`, `VPS_KNOWN_HOSTS`. No secret upload/key changes are performed in this session.
Public HTTPS, secure cookies, 14 screens, 1,000-payment/approval/replay/retry workflow and DB/audit
checks passed; app/worker/db are healthy. Public credentials are separate from local demo credentials:
retrieve privately from `/opt/reconflow/.secrets/demo-credentials.txt` via the trusted SSH alias,
or use local ignored `artifacts/vps-demo-credentials.txt`. Actual results: `docs/verification.md`.
