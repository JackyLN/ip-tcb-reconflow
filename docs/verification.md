# Verification record · 2026-11-06

MEASURED locally on macOS/Docker Desktop ARM64, Python 3.12; no external VPS or paid model calls.

- `make lint test`: Ruff check/format passed; 28 tests passed, one Starlette/httpx deprecation warning.
- `npm run check`, `npm run build`: JavaScript syntax and local Tailwind/vendor asset build passed.
- `docker compose build`: app/worker images built successfully with pinned Python/JS dependencies.
- Fresh `docker compose up -d db`, `make migrate`, first `make seed`: succeeded with new named volume.
  Later migration 0002 installed PostgreSQL append-only audit guard; no real production data existed.
- `docker compose up -d --wait`: app, worker, PostgreSQL and Caddy healthy (local HTTP, not TLS).
- `make smoke`: PostgreSQL HTTP flow passed: login, 1,000 payments, reconciliation findings, original
  import replay, simulated AI, supervisor approval, kill switch, injected failure/retry, 14 screens.
- `make eval`: 48 holdout cases contract-valid, deterministic fixture baseline 48/48, no failures;
  model accuracy/latency/abstentions null. This is not live model performance.
- `docker compose exec -T app python -m scripts.postgres_checks`: competing SKIP LOCKED claims,
  hash-chain verification and deployed audit UPDATE rejection passed. Temporary schema removed.
- `docker compose run --rm app python -m scripts.benchmark`: isolated 100/1,000/10,000 sources,
  one sample per size; raw measured results in benchmark.json. No human productivity measurement.
- `npm run browser`: passed desktop/mobile login, real Chart.js rendering, no page errors or CSP
  violations, all 14 screens. Visual review identified transient canvas resize overflow; a dedicated
  responsive container and explicit mobile bounds check passed the final run; screenshots visually
  inspected at 1440px desktop and 390px mobile (no mobile overflow).

NOT RUN/VERIFIED at this initial local checkpoint (VPS/TLS and CI are superseded by the later
2026-11-08 results below): public VPS/TLS, real stakeholder interviews, bank integrations, paid LLM inference,
independent security/accessibility audit, real worker process kill/restart drill (expired lease recovery
and injected failure tested), backup restore, hosted CI, actual human control experiment.

Final benchmark sample (1 CPU / 512 MB container, local PostgreSQL, ARM64): 100 payments / 5 payouts
import 22 ms + reconcile 13 ms; 1,000 / 50: 98 + 73 ms; 10,000 / 500: 1,047 + 815 ms. Single samples,
no distribution/generalization or human labor claim. Operations UI reports run time independently.

Final hardening: bounded account/provider lengths reject before PostgreSQL writes; successful
sign-ins clear attempt buckets; stale third leases dead-letter instead of retrying indefinitely;
audit append refreshes a cached control head after locking. Regression tests include these paths.

## Techcombank-inspired palette follow-up

MEASURED: `make test` 28 passed with the existing Starlette/httpx warning; `make lint`,
`npm run check`, `npm run build`, `docker compose up --build -d --wait`, `npm run browser`
and `make smoke` passed. All four services healthy. Existing end-to-end data/role/approval/replay
flows still operate. No live model call or model re-evaluation was needed for this presentation change.

Visually inspected screenshots: overview-desktop.png (1440px), overview-mobile.png (390px),
login-brand-desktop.png under ignored artifacts/. Additional actual Chromium check captured admin
controls hover and mobile login. No mobile overflow. Computed styles: primary background
rgb(204,23,32) with white text; danger hover rgb(116,21,28) with white text; sidebar focus
rgb(237,28,36). Brand chart reads #ED1C24 from CSS. No page errors/CSP violations across 14 screens.
Selected WCAG color-pair calculations and reference provenance are in ui-branding.md; full
independent accessibility and official brand-compliance audits were not conducted.

## Public VPS deployment · 2026-11-08 (Asia/Ho_Chi_Minh)

MEASURED on 187.127.220.131 (x86_64), source commit
31018ede59dcfd00701eb21471f60ab546be5140. Public URL: https://tcb.jackylenghia.com .

- Inspected the reference Lite Trading Bot CD, existing Docker networks/ports and shared Caddy.
  Backed up and validated a Caddy candidate before adding only the TCB hostname and reloading
  in place. Existing Caddy certificate volumes and both original site blocks were retained.
- `make lint test`: 28 passed; existing Starlette/httpx deprecation warning. `bash -n scripts/deploy.sh`
  and actionlint v1.7.7 against both workflow files passed.
- `docker compose --env-file .env.production -f compose.production.yaml config --quiet` passed.
- `bash scripts/deploy.sh <exact git SHA>`: build, isolated PostgreSQL startup, nonempty pg_dump,
  migrations, preserve-only seed, app/worker readiness and public HTTPS probe passed. Initial SHA
  label typo was corrected by rerunning with the value read directly from Git. Final recorded SHA
  and running image tags match the source above; credentials were preserved across the rerun.
- `.env.production` and generated account file mode 600; `.secrets/` mode 700. Secrets excluded from
  Git/build context and rsync. No deployment SSH key or GitHub secrets were uploaded/changed.
- Python default TLS trust/hostname validation succeeded: TLS 1.3, Let's Encrypt issuer YE2,
  DNS SAN tcb.jackylenghia.com, certificate expiry 2027-02-05 20:20:41 UTC. No insecure TLS flags.
- Public /login 200, /readyz 200; HTTP /login returns 308 to HTTPS. Session cookies inspected for
  Secure, HttpOnly and SameSite=Lax flags (values/tokens were not logged).
- `uv run python scripts/smoke.py --url https://tcb.jackylenghia.com --credentials artifacts/vps-demo-credentials.txt`
  passed actual public login, 1,000 payments, reconciliation, replay, SIMULATED investigation,
  independent supervisor approval, kill-switch toggle, injected failure/retry and 14 main routes.
- Production-container `python -m scripts.postgres_checks` passed competing claims, audit hash
  chain and audit UPDATE guard. `python -m reconflow.cli eval` stored 48/48 offline contract-valid
  holdout results, deterministic fixture baseline 48/48, live model scores null. No paid model calls.
- Chromium public HTTPS login/chart/14-screen check passed at 1440px desktop/390px mobile with
  no page/CSP errors or mobile overflow. Screenshots vps-overview-desktop.png/mobile.png in ignored
  artifacts; desktop image visually inspected.
- Existing Lite Trading Bot /api/health and Stayflow endpoints returned expected protected 401
  both before and after proxy reload/deployment. Their existing app containers remained healthy;
  their processes were not restarted by ReconFlow deployment.
- GitHub workflow CD is active/pushed. Hosted **verify** workflow for this exact deployed source
  succeeded: https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42415477106 .

NOT EXECUTED: hosted CD (user owns secret setup), database restore drill, live provider inference,
independent security assessment, stakeholder interviews or a real-bank pilot. Source remains a
synthetic demonstration. Latest subsequent documentation commit does not change deployed runtime code.

## GitHub Actions Node.js 24 maintenance · 2026-11-08

Reported CD run 42421131938 completed successfully (both verify/deploy); Node.js 20 messages were
deprecation warnings, not failed steps. Official action manifests were inspected at release tags:
checkout v7.0.1 and setup-uv v10.3.3 declare runs.using=node24. Both CI and CD now pin their exact
release commits: checkout 3d3c42e5aac5ba805825da76410c181273ba90b1 and setup-uv
68559e99cc807c1eb7e9238fd43a15bba460eec2. Installed uv stays 0.11.8; no app/runtime config changes.

Local `go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 .github/workflows/ci.yml .github/workflows/cd.yml`
and `make lint test` passed: 28 tests, one pre-existing Starlette/httpx warning. `git diff --check`
passed. Hosted verification completed successfully for workflow commit db64a57:
https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42421513904 . It ran the new checkout and
setup-uv actions, baseline lint/tests, Docker build/migrate/seed/start, smoke/eval and PostgreSQL
checks. Completed check-run 128550741336 has no Node.js 20 deprecation annotation; its only
annotation is an independent ubuntu-latest OS migration notice. The changed CD workflow has not
been dispatched again as part of this maintenance; start a new CD run from main to use it.
No production restart, paid model calls or secret changes were needed for this workflow change.

Sources: https://github.com/actions/checkout/releases/tag/v7.0.1 ,
https://github.com/astral-sh/setup-uv/releases/tag/v10.3.3 , and
https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/ .


## Public documentation · 2026-11-08

IMPLEMENTED: 22 curated pages under public-docs/, anonymous /docs/ reader, automatic nested
navigation, title search, heading outline, adjacent reading links, tables/tasks/footnotes/code and
local lazy-loaded Mermaid. Private docs/, environment files and operational runbooks are not
published. Only the reader allows Mermaid inline SVG styles; scripts remain self-only.

Observed local checks:
- `make lint test docs-check`: Ruff lint/format passed; 45 tests passed, one existing
  Starlette/httpx deprecation warning; all 22 pages and local document/heading links valid.
- `npm run check`, `npm run build`, `npm audit`: passed; zero npm audit vulnerabilities.
- `go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.7 .github/workflows/ci.yml .github/workflows/cd.yml`:
  passed. Bare `actionlint` is not installed on PATH; the pinned Go invocation is the successful check.
- `docker compose up --build -d --wait`: succeeded; app/worker/db/caddy healthy.
- `npm run docs:browser`: anonymous desktop/mobile reading, search, nested ADR and adjacent links,
  TOC, flow/state/sequence Mermaid, rich Markdown and no-JavaScript source fallback passed.
  No page/CSP errors, external asset requests or mobile page overflow. Reviewed screenshots in
  ignored artifacts/public-docs-{desktop,architecture,mobile}.png. Wide diagrams scroll internally.
- Full operations smoke against the normal local stack first failed at its SIMULATED assertion:
  the user's local provider is now configured and returned LIVE_FAILED_FALLBACK. This attempted
  configured inference; it is not a successful live evaluation or evidence of model quality.
  Do not run that smoke on a configured provider without explicit live-inference authorization.
- Reran with disposable project reconflow-docs-qa, its own PostgreSQL volume, generated credentials,
  and explicitly empty LLM_API_KEY/LLM_MODEL (verified booleans, no values logged). Initial QA proxy
  port override collided with inherited bindings; removed the override and used its env ports.
  Migration/seed and `uv run python scripts/smoke.py --url http://localhost:18080 --credentials artifacts/docs-qa.credentials`
  then passed: 1,000 payments, replay, simulated advisory AI, dual control, kill switch, retry and
  14 navigation screens. No-key regression does not measure live provider performance.

Hosted CI and deployed HTTPS publication results are recorded below after completion.
