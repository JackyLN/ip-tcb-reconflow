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

NOT RUN/VERIFIED: public VPS/TLS, real stakeholder interviews, bank integrations, paid LLM inference,
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
