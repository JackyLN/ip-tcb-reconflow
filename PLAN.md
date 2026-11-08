# ReconFlow — Product, Engineering & Delivery Plan

> Status: working prototype in verification; production/live-AI gates outstanding | Audience: Codex + candidate | Target: Techcombank AI Transformation Division Expert Challenge 2026
> Domain: Bank-side merchant settlement reconciliation and exception investigation, using synthetic/public data ONLY.

## Implementation progress (2026-11-06)

Authoritative scope above/below remains the target. Checked items describe implemented paths,
not a claim that every phase gate or challenge requirement is met.

- [x] Phase 1 audit: planning-only repository, no existing app or user changes; mapped screens/entities.
- [x] Foundation: Python 3.12 environment/lockfile, SQLAlchemy schema, explicit Alembic migration,
  Docker app/worker/PostgreSQL/Caddy, generated secrets/accounts, sessions/CSRF/RBAC, local assets.
- [x] Core: atomic CSV import, source hashes, deterministic scenarios (100/1,000/10,000), payout
  aggregation, conservative single-credit matches, persisted exceptions, proposals/dual control.
- [x] Durable jobs: DB leases/row locks, retry/backoff, expired lease recovery, failure injection,
  heartbeat/in-app alerts, application append-only audit hash chain.
- [x] AI: four read-only tools, schema/citation membership checks, quotas, advisory-only reports,
  explicit simulated no-key mode, configurable HTTP adapter and human fallback, kill switch.
- [x] Evaluation runner: 72 labeled fixtures (24 development/48 holdout), offline contract checks,
  explicit live mode and scoped accounting; 48-case measured run: 18/48 (37.5%).
- [x] UI: all 14 navigation screens, import/run/payout/case detail, human review actions,
  measured snapshot KPIs, editable assumption-based USD impact, architecture/rollout viewer.
- [x] Local unit/API verification: `make lint test` passed, 28 tests at hardening checkpoint.
- [x] Initial Docker build, clean PostgreSQL migration and seed succeeded.
- [x] Docker HTTP walkthrough, PostgreSQL competing claims/audit guard and isolated benchmark.
- [x] Chromium desktop/mobile rendering, chart bounds, no page/CSP errors and 14 screens verified.
- [x] One recorded provider-backed investigation: case #1 / investigation #2, LIVE; separate supervisor escalation.
- [x] Real paid 48-case holdout: 18/48 correct, 47/48 schema/citation valid; all 30 failures published.
- [ ] Five stakeholder interviews across three roles (not conducted; A1 not met).
- [x] External VPS/domain/TLS fresh install and live demo verified at https://tcb.jackylenghia.com.
- [x] Actual browser walkthrough video recorded (87 seconds, synthetic flow; no narration).
- [ ] Full SLA/period reporting, human-control study, semantic hallucination grading, rework/ramp ROI.
- [ ] Bank production security: SSO/MFA, tenant scopes, separate DB roles, external audit anchoring,
  secrets management, restore drill and independent security review.

Implementation decisions/deviations: one synthetic merchant workspace; cumulative refunds stored
on payment lines and fee/adjustment on payouts rather than separate ledgers. Stable internal integer
IDs plus source IDs replace planned UUIDs. Provider profiles are immutable via UI; use distinct names
for new policies. Four combined tools include refunds/fees in payout aggregates. No external alerts,
partial settlements or live integrations. Operations north-star is a labeled current-snapshot proxy,
not full within-SLA performance. Business impact is annual constant assumptions, not monthly ramp.
External model calls can repeat after a crash; financial DB effects remain atomic/idempotent.
These simplifications do not meet all original Definition of Done items. See README known gaps.

Final local acceptance checkpoint: `make lint test` 28 passed (one dependency deprecation warning),
`npm run check/build/browser`, Docker build/start/migrate/seed/HTTP smoke and offline eval passed.
All four services healthy. 48/48 simulated contract checks, no live model scores. PostgreSQL locking,
audit hash-chain/UPDATE guard passed; measured 10,000-payment/500-payout reconcile sample 815 ms.
See docs/verification.md for exact scope, omissions and source benchmark artifact.

## UI branding update (2026-11-06)

- [x] Audited existing shared CSS, templates and Chart.js configuration; retained existing flows.
- [x] Implemented user-requested Techcombank-inspired red/black/white/neutral palette with restrained gold.
  Exact brand red #ED1C24 for graphical accents; darker #CC1720 actions and #B5121B links/focus
  for text contrast. Gold #B18A49 is a chosen UI accent, not a verified official gold hex.
- [x] Verified built desktop/mobile screens, login/controls hover and keyboard focus, selected
  contrast pairs, 28 existing tests, lint/JS checks, Docker health and full HTTP smoke.

Changes scoped to reconflow/static/app.css, app.js, measured badge class and project documentation.
No official Techcombank logo/affiliation is introduced. Prior navy/teal direction is superseded by
this explicit user request. Acceptance: no navy/teal accents remain, accessible text/focus colors,
real chart data, no desktop/mobile overflow, main routes and persistent workflow still operate.

## VPS deployment phase (2026-11-08)

- [x] Inspected reference Lite Trading Bot CD workflow, server containers, ports, shared Caddy and DNS.
- [x] Added production Compose (no public container ports), shared-Caddy snippet, secure bootstrap,
  backup/migrate/seed/readiness deployment script and manual GitHub Actions CD workflow.
- [x] Verified code/config and deployed isolated ReconFlow database/app/worker at /opt/reconflow.
- [x] Added/validated only tcb.jackylenghia.com on shared Caddy; trusted Let's Encrypt HTTPS verified.
- [x] Public synthetic workflow/browser/DB/offline eval checks passed; existing applications retained
  their expected HTTP 401 protected responses. Deployment source CI passed on GitHub.
- [x] User-configured GitHub Actions CD succeeded: run 42421131938 (verify and deploy).

User chose tcb.jackylenghia.com and explicitly reserved GitHub secret/key setup for themselves.
Existing shared Caddy owns 80/443; standalone ReconFlow Caddy is omitted on this VPS. App joins
stayflow_backend as reconflow-app, with separate private reconflow backend/database volume.
Changes: compose.production.yaml, deploy/Caddyfile.snippet, scripts/configure_production.py,
scripts/deploy.sh, .github/workflows/cd.yml, secret/build exclusions and operational documentation.
Acceptance: valid configs, baseline tests, app/worker/db healthy, safe migration/seed/replay,
valid public certificate, secure cookies, and no regression in Stayflow/Lite Trading Bot routing.

Verified deployment: commit 31018ede59dcfd00701eb21471f60ab546be5140; app/worker/db healthy,
HTTP redirects to HTTPS (308), Secure/HttpOnly/SameSite=Lax cookies, certificate hostname/trust
verified (expiry 2027-02-05 UTC). Public 1,000-payment/replay/AI/dual-control/retry smoke and all
14 browser screens passed. Credentials preserved across deployment rerun; backups nonempty.
GitHub CI run 42415477106 succeeded. Subsequent user-configured hosted CD run 42421131938
succeeded; its Node.js 20 deprecation warnings are addressed by the maintenance phase below.

## Actions runtime maintenance (2026-11-08)

- [x] Inspect reported CD run 42421131938: verify/deploy both succeeded; Node.js 20 messages are warnings.
- [x] Verify official release manifests: checkout v7.0.1 and setup-uv v10.3.3 both declare node24.
- [x] Update all checkout/setup-uv references in both CI and CD to exact release commit SHAs.
  Keep installed uv CLI version 0.11.8 and the application/deployment commands unchanged.
- [x] actionlint v1.7.7 and baseline lint/tests passed (28 tests; existing TestClient warning).
- [x] Hosted CI 42421513904 passed with the updated action references; completed check annotations
  contain no Node.js 20 warning (only a separate hosted-runner OS migration notice).

Files: .github/workflows/ci.yml, .github/workflows/cd.yml, README.md, docs/ai-log.md and
verification notes. Acceptance: official Node.js 24 action runtimes, valid YAML/workflow expressions,
baseline checks pass, hosted actions run with updated references and no Node.js 20 warning.
No secrets are read/changed, no paid model evaluation and no production redeployment are required
for this workflow-only change. Start a new CD run from main to use the new workflow; re-running
an older run retains that run's workflow revision.

## Public documentation phase (2026-11-08)

- [x] Review internal docs and curate a public-only source tree at public-docs/ (22 Markdown pages).
- [x] Add markdown-it-py, plugins/Pygments and locally bundled Mermaid for a FastAPI /docs/ reader.
- [x] Add automatic nested catalog/navigation, heading outline, sibling links, previous/next,
  title search, login/sidebar entry points and documented authoring conventions.
- [x] Verify anonymous access, no private/traversal/symlink exposure, safe Markdown rendering,
  public-only CSP style exception, rich features, Mermaid browser rendering and mobile layout.
- [x] Run baseline/unit/API checks and isolated no-key Docker smoke/build.
- [x] Publish the new public route and verify anonymous HTTPS reading.

Files/dependencies: public-docs/, public renderer service/router/templates/CSS, frontend/docs.js,
Python Markdown dependencies and pinned Mermaid/esbuild npm packages, Docker/asset build wiring,
publication checks/tests, README and AI log. Only content deliberately placed in public-docs/ is
published; internal runbooks, server environment/configuration and credentials remain excluded.
This public subset is curated; maintainers update its counterpart when changing a shared decision.
No finance/authentication/AI investigation behavior changes and no paid inference is needed.

Verified source a489abeea12a3edd4dfd4557139e7e20c600f675 is deployed. All 22 public HTTPS pages,
private-path 404s, readiness/protected console and anonymous browser checks passed.
Local lint/45 tests, publication checks, Docker health and isolated no-key workflow smoke passed.
Hosted CI 42424030055 passed the fresh Docker workflow/offline evaluation and PostgreSQL checks.

## 0. North star and non-negotiables

Build an interview-ready **working banking operations product**, not a static dashboard, a generic chat assistant, or a fake demo. An interviewer should be able to sign in, load a deterministic scenario, import or inspect records, run reconciliation, investigate mismatches with bounded AI, make role-gated human decisions, see a complete audit trail, simulate failure/re-run and view measured analytics and AI evaluation.

**North Star Metric:** percentage of eligible settlement batches fully reconciled or routed to a documented, owned exception within the target SLA, with no unauthorized automated financial changes. Show denominator, numerator and time window.

Do not claim bank-specific facts, real financial results, model evaluation outcomes or five stakeholder interviews unless verified. All demo datasets and projections must be labeled synthetic/assumptions. Never use real customer data or secrets in commits.

## 1. Problem framing and product boundary

**Problem hypothesis:** bank merchant-payment operations need to reconcile gateway/payment-provider payout breakdowns to bank credits; disagreements due to fees, refunds, timing, missing/duplicate entries or references consume manual effort and increase unresolved-case risk. This is a hypothesis requiring validation with Techcombank stakeholders; do not imply knowledge of internal workflows.

**Customer / users:** operations analyst (investigate), supervisor (review/approve), operations manager (metrics), risk/compliance auditor (read audit), platform administrator (configuration and controls). External merchant and bank integrations are out of MVP scope.

**End-to-end vertical slice:** create synthetic payments -> group by payout -> provider payout/fee/refund data -> bank account credits -> reconcile -> exception -> AI read-only investigation -> review queue -> authorized human decision -> audit and analytics.

**Financial model:** individual payments are many-to-one with provider payouts. Payouts correspond to bank credits under explicit assumptions; partial payouts, multiple bank credits and complex cross-currency settlement are NOT supported in MVP, and must be marked unsupported rather than falsely matched. Preserve raw imported data and provenance. Store integer minor units and ISO 4217 currency; VND exponent 0 and USD exponent 2. Fee/refund arithmetic deterministic; rounding explicit.

**In scope:** one merchant/bank-facing simulated workflow with multiple providers, CSV import, seed scenario generator, reconciliation, exceptions, AI investigation, maker-checker approvals, notifications inside app, durable jobs, immutable audit events, analytics and repeatable AI evaluation.

**Out of scope:** payment execution, custody, real bank transfers, actual Techcombank integrations, autonomous accounting adjustments, real-time fraud detection, real KYC, live Stripe transactions, fine-tuning, Kafka, n8n, Kubernetes, production banking certification.

## 2. Assignment coverage (traceability)

| Brief requirement | Product / artifact | Proof in demo |
| --- | --- | --- |
| A1: >=5 stakeholders across >=3 roles, conflicts | `docs/discovery.md` interview tracker and honest assumptions | Recorded interviews only if actually conducted, otherwise plainly marked outstanding |
| A2: 12-month business case, assumptions/sensitivity | `docs/business-case.md`, `/reports/impact` | Adjustable volumes, minutes, cost, adoption, exception rates, AI costs, net value |
| A3: problem statement; >=3 directions incl. build, buy, do nothing; 1-page decision memo | `docs/decision-memo.md` | 1-page PDF-ready narrative, clear rejected alternatives |
| A4: 90-day success and stop criteria | `docs/decision-memo.md` + `/reports/impact` | Explicit measurable pilot thresholds and kill/stop criteria |
| B1: full prototype and production scale architecture, 2–3 tradeoffs, privacy/auth/audit | Running app, `docs/architecture.md`, `docs/adr/` | Interactive workflow, architecture diagram, classification, RBAC, event logs |
| B2: AI quality, failures, latency, cost | `/ai/evaluation`, `docs/evaluation.md` | Measured labeled holdout results incl. unsupported claims and abstentions |
| B3: one north star and 2–3 supporting metrics, pilot/A-B | `/reports/operations`, `docs/metrics.md` | Calculated SQL-based measures and experiment design |
| B4: 3-month team-of-five rollout | `docs/rollout.md` | Roles, phases, dependencies, risks, milestones |
| C1: safe-to-rerun automation, monitor/alert, kill switch | Worker, jobs, app controls | Duplicate upload/job rerun and injected failure; alert displayed; pause new AI jobs |
| C2: before/after measured then projected at scale | `/reports/impact` and benchmark tests | Measured processing benchmarks versus assumptions clearly distinguished |
| C3: confidence, human queue, audit, harm if wrong | `/exceptions`, `/review`, `/audit` | Explainable evidence, mandatory human decisions, policy controls, failure modes |
| C4: reusable configurations/templates/docs | Provider config, scenario config, `docs/adoption.md` | Create second provider profile; import template; replay scenario |
| AI log (5–10 prompts, errors, fixes) | `docs/ai-log.md` | Genuine log captured during development |
| Live tradeoff + code change | `docs/demo-script.md` | Small controlled rule/config change with test |
| Submission | README, deployed link/video, repo, docs | 15-min presentation + 15-min Q&A, 5-min demo video optional |

## 3. User experience and navigation

- Professional, elegant, responsive light-first banking operations UI with charcoal/black typography, Techcombank-inspired red (#ED1C24), white/sky-grey surfaces and restrained gold accents (user-directed palette update), high contrast, clear table density, no gimmicky gradients. Create a coherent design system and accessible states.
- Sidebar: Overview; Data Sources & Imports; Reconciliation Runs; Transactions & Payouts; Exceptions; AI Investigations; Review Queue; Reports (Operations / Business Impact / AI Evaluation); Audit Trail; Configuration & Controls.
- Dashboard shows *actual database-calculated* KPIs, latest run, exception distribution, throughput, SLA, and action items; label synthetic environment prominently.
- Scenario launcher with three scenarios: (1) clean payout; (2) mismatches, fees, refunds, missing bank credit, duplicates; (3) interrupted worker/replay/kill switch. Show before/after impacts and explain outcomes.
- Drilldown: payment -> payout -> bank credit -> matching evidence -> exception -> AI report -> reviewer history; persist state and allow page refresh.
- Analyst can investigate and submit recommended case resolution; supervisor can approve/reject. Admin can pause/resume AI jobs. Auditor read-only. User roles are server enforced, not UI-only. Clearly show what cannot be auto-approved.
- Demo accounts seeded only behind `DEMO_MODE=true`, with environment-defined one-time passwords or generated passwords printed once to deployment logs; never publish fixed passwords in repository. Demo role-switching must still use authenticated sessions, not insecure role headers.

## 4. Technical architecture

### Stack
- Python 3.12+, FastAPI, Jinja2, HTMX, Alpine.js (only if needed), locally built Tailwind CSS, Chart.js; frontend assets pinned and served locally. No frontend SPA required.
- SQLAlchemy 2 async or sync consistently; Alembic; PostgreSQL 16+; Pydantic v2; pytest; Ruff; mypy optional.
- Separate Python worker using DB-backed jobs and `FOR UPDATE SKIP LOCKED`, visibility/lease timeout, retries/backoff, dead-letter status. Explicit claim/reclaim logic and idempotent job handlers. Use DB advisory locks or unique constraints where appropriate.
- OpenAI-compatible model API adapter using environment-configured URL/model/key (or provider SDK); HTTP timeout/retry; structured schema validation; never log API keys or full prompts containing sensitive data.
- Docker Compose: `app`, `worker`, `db`, `caddy` (HTTPS, reverse proxy); DB on private network, only Caddy public. Persistent volumes; healthchecks; migrations via one-off command. Resource bounds and log rotation.

### Core entities (adapt as necessary)
`User`, `Role`, `Merchant`, `ProviderProfile`, `ImportBatch`, `Payment`, `Refund`, `ProviderPayout`, `PayoutLine`, `FeeAdjustment`, `BankCredit`, `ReconciliationRun`, `ReconciliationMatch`, `ExceptionCase`, `Investigation`, `EvidenceReference`, `ReviewDecision`, `Job`, `AuditEvent`, `ModelInvocation`, `EvaluationDataset`, `EvaluationRun`, `EvaluationCaseResult`, `AutomationControl`.

### State machines
- Import: `RECEIVED -> VALIDATING -> READY / REJECTED`
- Reconciliation: `QUEUED -> RUNNING -> COMPLETED / PARTIAL / FAILED`
- Exception: `OPEN -> INVESTIGATING -> NEEDS_REVIEW -> RESOLVED / ESCALATED` (permitted transitions enforced)
- Review: `PENDING -> APPROVED / REJECTED / ESCALATED`; reviewer cannot approve own submitted proposal.
- Job: `PENDING -> LEASED -> COMPLETED / RETRY_WAIT / DEAD_LETTER`; lease expiry recoverable.

### Money, time, IDs
- Amounts integer minor units; currency exponent explicit; no floating-point money.
- Time stored UTC and shown with timezone in UI; timestamps deterministic in fixtures and relative within current demo run where possible.
- Stable UUIDs and external source IDs; multi-record payout sums and expected bank net are deterministic; unique constraints on `(provider, external_id, source_type)` and relevant batch keys.

### Reconciliation engine
1. Normalize and validate source schemas; reject/quarantine malformed rows, don't silently drop them.
2. Aggregate payments, refunds, provider fees and adjustments by payout ID.
3. Calculate expected net using policy version, currency, evidence and timestamp windows.
4. Match provider payout to eligible bank credits by reference, currency, account, amount and timing, with clear tiers (exact; explainable difference; unresolved/ambiguous).
5. Never force a many-to-many ambiguous match; use human review.
6. Persist deterministic rule version, input hashes, match rationale, provenance and audit event.
7. Import and reconciliation are replayable; repeated same source batch produces no duplicate financial records or repeated approved actions.

## 5. AI investigation design

### Model selection decision (2026-11-08)

- [x] Record accepted GPT-5.4 mini target (`gpt-5.4-mini-2026-03-17`) in
  [ADR 004](docs/adr/004-demo-llm-selection.md), README and evaluation guidance.
- [x] Record dated standard token-price assumptions (USD 0.75 input / 4.50 output per million),
  version pinning rationale and unchanged deterministic-finance/advisory-only policy.
- [x] Implement/test `max_completion_tokens` request parameter and explicit `reasoning_effort: none`.
- [x] Verify account availability/live compatibility and observe single-demo latency/usage/cost.
- [x] Measure exact-label holdout performance, abstention, latency/cost and explain failures.
- [ ] Independent blinded semantic/unsupported-claim and bank-risk grading.

The initial selection phase edited documentation only: docs/adr/004-demo-llm-selection.md, docs/evaluation.md,
README.md, PLAN.md and docs/ai-log.md. Acceptance: consistent target/rates, official source links,
clear distinction between accepted decision and pending implementation/evaluation. No live
inference, secrets edit, runtime change or deployment was performed for that initial update.
The subsequent recorded-demo phase above implements and verifies the adapter contract.


**Why AI:** assists with contextual diagnosis and explanation when records and provider policies are incomplete or ambiguous. It does not decide matching arithmetic, ledger adjustments, transfers, approval or risk compliance.

**Inputs:** scoped case summary, structured evidence IDs, limited retrieved records, policy/playbook version. Tool output is untrusted data; never follow instructions embedded in notes or imported CSV.

**Read-only tools:** `get_case`, `get_payment_and_payout`, `get_fee_adjustments`, `get_refunds`, `find_candidate_bank_credits`, `get_provider_policy`. Tools must enforce merchant/role scope and query-size bounds. No arbitrary SQL or HTTP requests from the model.

**Playbooks:** missing settlement, fee mismatch, duplicate candidate, refund reversal, late settlement, insufficient evidence.

**Agent bounds:** <=4 tool calls, fixed token/time budgets, model retry bounded, JSON schema enforced, evidence IDs verified against retrieved records, prompt-injection defenses, reason/result captured with prompt/model versions. Graceful fallback: case stays in review queue if model unavailable.

**Output:** `{exception_id, classification, summary, confirmed_facts[], hypotheses[], missing_evidence[], evidence_refs[], recommended_next_step, confidence_band, requires_human_review}`. Confidence is uncalibrated unless evaluated; backend independently decides review necessity. All recommendations advisory.

**AI budget:** cap calls per run/user/day; queue jobs; audit token/cost estimates from actual provider usage; no uncontrolled batch calls. Explicit offline/no-key demo with cached **labeled prerecorded output** (not falsely presented as live model output).

## 6. Evaluation and reliability

- Synthetic seeded labeled dataset with >=60 cases and fixed seeds; separate development and holdout sets; include clean, fee/refund, missing, duplicates, ambiguous, delayed, insufficient-evidence, contradictory and adversarial prompt-injection cases.
- Compare deterministic-only baseline to AI-supported workflow. Never present seeded expected labels as model scores.
- Compute root-cause accuracy (only cases with determinable labels), evidence validity, hallucination/unsupported-claim rate, high-risk escalation recall, abstention quality, p50/p95 latency and observed price per investigation. Display confusion matrix where useful. Report sample size and uncertainty; show all failed cases and traces, with redaction.
- Test idempotency, concurrent job claiming, duplicate webhook/import, retry after crash, RBAC, CSRF/session, input validation, financial math, audit immutability, AI schema failure, unverifiable citations, no-model fallback, kill switch.
- Add `make test`, `make lint`, `make seed`, `make eval` (live eval optional; never execute paid API calls implicitly), `make smoke`.

## 7. Analytics and business case

### Operations report (measured)
- Total payments, payout batches, reconciliation completion, unresolved exception count/severity, median processing runtime, throughput, exception aging, review turnaround and SLA metrics; all computed from stored demo records.
- Show at least one benchmark of automatic processing time under a known instance size and dataset; clearly distinguish system processing from assumed human labor savings.

### Business impact (assumptions + sensitivity)
- Editable assumptions: monthly payout volumes, manual investigation minutes, automated proportion, per-hour loaded cost, AI cost, adoption percentage, training/implementation costs and quality/rework rates.
- 12-month gross capacity value, total cost, net benefit and sensitivity of assumptions. Use low/base/high cases and identify break-even; distinguish capacity freed from realized savings and revenue. Never assert Techcombank data is known.

### Proposed pilot KPIs
- North star as above; supporting: exception investigation turnaround, audit-complete resolution rate, AI evidence-validity rate. Targets must be labelled proposed, not achieved.
- 90-day pilot with control group or staged rollout and clear stop conditions (e.g., materially unsupported AI claims, unauthorized actions, significant reconciliation error or negative risk-adjusted net benefit).

## 8. Security, operations and governance

- Data classes: public synthetic demo; in real deployment: financial confidential and personal data. Explicit threat model and data-retention assumptions.
- Strong session auth; Argon2/bcrypt password hashes; CSRF protection for mutating web forms; RBAC on server; scoped queries; validated file upload, size/type caps, CSV formula injection-safe exports; no dynamic SQL from LLM; parameterized DB queries.
- HTTPS with Caddy; `.env.example` not `.env`; secrets supplied only at runtime; DB not internet-exposed; least privilege; bounded AI endpoints and rate limiting; structured logs redact PII/secrets.
- Append-only, tamper-evident audit event chain (hash chaining optional, document its limitations), actor/time/action/entity/old/new/policy version; no admin UI deleting audit history.
- Kill switch for NEW AI investigations and optionally auto-routing; deterministic reconciliation can continue. Real rollback = disable new operations and safely retry/replay; do not pretend to undo external bank transfers.
- Health/readiness endpoints, worker heartbeat, stuck-job alerts, processing error alerts, simple `/operations/health` page.

## 9. Explicit decision records

Document at least three ADRs:
1. Modular monolith + DB-queued worker vs distributed microservices/Celery/n8n (cost/deployment/consistency).
2. Deterministic reconciliation + bounded AI investigator vs LLM deciding financial truth (accuracy/risk).
3. Bank-first synthetic data + reproducible fixtures vs live Stripe integration (privacy/demo reliability/realism).

## 10. Implementation phases and acceptance gates

### Day 1 — Foundation, domain and traceability
- Repository structure; `AGENTS.md`, `AGENT.md`, `PLAN.md`, `README.md`, `.env.example`, Docker Compose, migrations, auth/RBAC, design system, synthetic data model, deterministic generator with one-to-many payment-to-payout linkage.
- Create docs skeletons: discovery, memo, business case, architecture, metrics, AI log, rollout, demo.
- Gate: `docker compose up --build` launches; `make seed` creates coherent source records; web login and dashboard work; `make test` passes.

### Day 2 — Genuine core workflow
- CSV import and validation, reconciliation algorithm, persisted runs and matches, exception detection, interactive drilldown, human review workflow, audit, repeat-safe automation, robust worker.
- Gate: clean and mismatch scenarios produce verifiable results; duplicate import/re-run do not double count; analyst cannot self-approve; failure-retry works.

### Day 3 — AI, evaluation and operations
- Provider-configurable LLM adapter; scoped tools, playbooks, structured outputs, evidence checks, human escalation, AI invocation trace, kill switch, labeled test set, evaluation runner; reports of real results, not placeholders.
- Gate: one model-backed investigation and one failure fallback end-to-end; evaluation runs with clear cost/latency/failures; test suite passes without requiring a paid key.

### Day 4 — Business reporting, hardening and deployment
- Business impact sensitivity, operations/AI dashboards, process timings, 90-day rollout and decision memo, security review, CI, VPS Caddy/TLS deployment guide, demo walkthrough, usability/accessibility fixes, smoke test on freshly provisioned VPS.
- Gate: external demo URL works; app can be used without technical assistance; 5-min demo path and 15-min interview narrative complete; honest outstanding items in README.

## 11. Five-person 90-day rollout (proposed, not completed)

Team: Product/BA (1), backend/data (1), AI/ML (1), frontend/UX (1), platform/security/QA (1), with bank operations/risk stakeholders participating as reviewers.
- Days 1–30: discovery, secure integration plan, historical baseline, small shadow pilot and control group; risk approvals.
- Days 31–60: single-team supervised pilot, compare baseline, refine fee policies and exception categories, train users; monitor incident and quality.
- Days 61–90: phased expansion across additional payout sources/teams if pilot gates pass, operational handoff and change management.

## 12. Interview demonstration (8–10 minutes of app within 15-minute presentation)

1. Product decision: who suffers, why now, alternatives, estimated ROI and caveats.
2. Launch realistic synthetic scenario with 1,000 payments grouped into payouts.
3. Open run; show matched vs unresolved and evidence for one payout.
4. Open a discrepancy; launch bounded AI investigation; show evidence tools, hypothesis and missing proof.
5. Analyst submits recommendation; supervisor reviews and approves/rejects; audit shows actors/actions.
6. Re-run same batch; demonstrate idempotency; toggle kill switch and show AI disabled while deterministic matching remains safe.
7. Open AI evaluation with actual test size, error cases, costs/latency; compare baseline; show business sensitivity.
8. Show production target architecture, trade-offs, 90-day plan and stop criteria.
9. Live-change ready: change one fee tolerance/provider config or rule test, rerun targeted tests and demonstrate difference.

## 13. Remaining questions and transparent assumptions

- Confirm Techcombank owns the proposed merchant-settlement exception workflow; no internal operational claims until validated.
- Secure five genuine stakeholder conversations or explicitly state discovery limitation.
- Confirm public benchmark dataset permissions before inclusion; synthetic generator must make demo fully independent of downloads.
- Decide model vendor and live API budget; never lock business logic to one provider.
- Production banking controls described as *target state*, not falsely claimed MVP certifications.

## 14. Definition of done

All visible dashboard figures trace to persistent source records or visibly labeled assumptions. Every main navigation route loads, imports and jobs are real, reviewer permissions are enforced, at least one AI invocation has a verifiable evidence trail, evaluation is reproducible, seeds reset safely, Docker fresh-install works, tests/README/docs reflect reality, and presentation can clearly show what is built vs planned.


## Recorded live demonstration phase (2026-11-08)

User authorized use of deployed credentials/key for one flow and requested a video of actual
actions. Intended files: AI adapter and mocked request tests, replayable browser recording script,
README/PLAN/AI log/ADR and observed verification notes. Dependencies: existing Playwright browser
recording, private generated demo credentials and configured provider; no new paid service.
Acceptance: baseline tests pass without a key; deploy preserves server environment; one scoped
synthetic case is investigated, actual mode/usage/evidence recorded, separate maker/checker
review shown, video inspected and delivered without secrets. This is not a holdout evaluation.

Recorded demonstration outcome: deployed 6d44ecc98793b2de137f848722380091cf4d9593;
46 local tests/lint and hosted CI 42425049643 passed (including fresh Docker smoke/eval/DB checks).
Case #1/investigation #2 LIVE: four observed tools, two provider requests, 1,779 input/458 output
tokens, summed request latency 7,608 ms, estimated USD 0.00339525. Analyst #1 proposed and
supervisor #2 escalated proposal #2. Video is 87 seconds, converted to H.264 MP4 and sampled
visually. Initial recording failed before queueing AI due to an HTMX caption replacement; fixed
and reran. Exactly one paid investigation queued. Holdout/semantic evaluation remains unmeasured.


## Public video documentation phase (2026-11-08)

Intended files: public product/demo Markdown README, existing reviewed MP4 under public assets,
reader support for a constrained local-video fence, navigation/authoring notes, media checks and
README/AI log. No new dependency or model call. Acceptance: anonymous watch/download, chapters
and measured/estimated labels, safe local-only video rendering, byte-range playback, mobile fit,
publication/API/browser checks and deployment preserving environment. Existing recording is reused.

- [x] Publishable video README/chapters/outcome/usage and native local-only MP4 player.
- [x] Local lint/51 tests, 23-page validation, JS syntax checks and Docker health.
- [x] Anonymous browser playback/seeking, desktop/mobile layout and no page/CSP errors.
- [x] Deploy and verify anonymous HTTPS playback/download.

Hosted CI 42425952741 passed the public-video source, including clean Docker offline workflow/DB checks.


## Graded 48-case live holdout phase (2026-11-08)

User explicitly requested and authorized a real graded 48-case provider evaluation, dashboard
results and failure explanations; this implements outstanding B2/section 6 acceptance. Freeze
synthetic-v1 fixtures and investigator-v1 prompt before calling the provider. Intended files:
evaluation runner, adapter evaluation capture, explicit CLI checkpointing, dashboard partial,
mocked grading/accounting/API tests, README/evaluation/failure-analysis/public docs and AI log.
No new dependency or mandatory paid baseline test. Persist per-case outputs, traces, invocation
IDs, actual usage and configured-rate estimates, completion status and dataset/prompt hashes.
Acceptance: no-key regression passes; one bounded sequential 48-case live run; dashboard verified;
all observed failures explained without hiding errors or substituting offline output. Exact-label
grading is separate from independent semantic/hallucination grading and bank-domain generalization.


Holdout outcome: production evaluation #2 on source cc3c2e1c1fafbefa3fda3218201d4d1e65ff86a0
completed all 48 cases without retries. Correct 18/48, valid 47/48, 29 accepted wrong labels +
one citation rejection, no abstentions; deterministic fixture baseline 48/48. p50/p95 3,369/4,582
ms; 96 requests, 82,342 input/20,290 output tokens, estimated USD 0.15306150. Full snapshot and
progress synchronized locally; imported locally with remapped request IDs and no finance writes.
Public all-failures report/JSON/log prepared; exact-label grading does not fulfill independent
semantic/hallucination or high-risk-recall targets. No prompt/model change or extra paid run.

- [x] Freeze fixture/instruction hashes and run the authorized 48-case batch once on VPS.
- [x] Sync original results/progress/request snapshot locally and import without inference.
- [x] Independent reference/count/cost checks; 59 regression tests, 24-page link checks.
- [x] Prepare public full results, 30 failure explanations and synthetic machine-readable evidence.
- [x] Verify final deployed authenticated dashboard/mobile and anonymous reviewer report/downloads.

Final source ab91db1465eed4b248f97ab9cd76e53a7a0a111e deployed and healthy; CI 42429726168
passed 59 tests, 24-page validation and fresh Docker/offline workflow/PostgreSQL checks.
Public report/snapshot/progress and authenticated dashboard verified over HTTPS on desktop/mobile.
