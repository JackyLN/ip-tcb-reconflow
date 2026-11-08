# Actual AI-assisted development log

Date: 2026-11-06. This is one development session, not invented stakeholder conversations or
seven independent user turns. Entries quote actual user requests or embedded project instructions
that materially directed the implementation. No live model/provider evaluation was performed.

1. User: “read CODEX_MASTER_PROMPT.md instruction for the reconflow project”. Read that file,
   PLAN.md and AGENTS.md in full; returned acknowledgment without edits.
2. User: “follow CODEX_MASTER_PROMPT.md and setup the project as instruct”. Inspected repository,
   README/AGENT, Git status and toolchain. Found planning-only files, no app or user code changes.
3. Embedded master prompt: “First return a concise inspection and implementation outline; then act
   on it instead of writing only a plan.” Created Python app, schema, migrations, Docker services,
   tests and actual UI. Kept services separate from HTTP adapters and did not stop after scaffolding.
4. AGENTS instruction: “Always use integer minor units for money with currency-specific exponent”.
   Implemented Decimal display/input, integer payout fee rounding and multi-payment aggregation;
   tested refund/net math. Later added a cross-provider shared-reference ambiguity regression test.
5. Embedded master prompt: “Server must prevent self-approval.” Implemented server role/CSRF gates,
   service-level maker-checker transitions and UI role affordances; tested auditor denial and
   supervisor self-decision rejection. Human closure never mutates finance source records.
6. Embedded master prompt: “graceful no-key/prerecorded mode labelled as such”. Implemented
   SIMULATED reports, four read-only tools, evidence/schema policy, kill switch, quotas and actual
   HTTP usage records. Offline eval returned 48/48 contract-valid outputs; model scores stay null.
   Mocked provider tests cover unobserved evidence, arbitrary SQL tool rejection and call bounds.
7. Embedded master prompt: “Tell me what has NOT been implemented or verified.” Wrote explicit
   gaps for interviews, real bank evidence, live inference, semantic hallucination grading,
   external TLS/VPS, SLA reporting and production security. No fabricated discovery or ROI results.

Actual failures/corrections:
- Initial pytest could not import reconflow. Added explicit repository pythonpath to pytest config.
- Initial Ruff pass found formatting/import and duplicate-key issues. Corrected and reran checks.
- Initial draft migration depended on mutable ORM metadata. Replaced it with explicit Alembic schema.
- Caddy healthcheck resolved localhost to an unsuitable loopback. Used 127.0.0.1; all four services
  subsequently reported healthy. No DNS/TLS success is inferred from local HTTP.
- Browser checks found an app.js syntax error and HTMX inline-style CSP violation missed by API tests.
  Rewrote chart initialization, disabled HTMX injected styles/eval, added `npm run check`, and reran
  browser verification. Repeated QA sign-ins also exposed successful-logins accumulating in the
  throttle bucket; success now clears its bucket. Failed-attempt throttling remains tested.
- Final audit review found that a previously cached control row could retain a stale hash head.
  Refreshing the row after locking and a regression test protect chain continuity. Third expired
  leases now dead-letter instead of allowing unbounded crash-recovery attempts.

Reflection: the deterministic DB workflow and honest labels provide a stronger demo than invented
model metrics. API tests alone missed JavaScript rendering problems; browser checks are necessary.
Schema/citation membership cannot establish semantic truth, and small synthetic tests cannot establish
bank-domain safety. Single-workspace shortcuts and unverified external integrations remain explicit.
See verification.md for exact final checks, observed benchmark and omissions.

8. User follow-up: “regarding the UI, refering techcombank branding color to re-update the UI.”
   Read the supplied brand-manual/secondary references and checked the official public brand site.
   Replaced navy/teal with red/black/white/neutral tokens, adapted action red for text contrast,
   added restrained gold and connected Chart.js to the shared brand token. Existing product
   workflows and the ReconFlow synthetic-demo identity are retained. Exact gold is a UI choice,
   not a fabricated official specification. Contrast and final browser/build outcomes are in
   verification.md. No live AI inference was required or performed for this UI update.

9. User requested VPS deployment via `ssh jackylenghia`, checking reverse proxy/HTTPS and adding a
   GitHub deployment workflow based on Lite Trading Bot. Inspected that workflow and the live VPS:
   existing shared Stayflow Caddy owns 80/443, so a second public proxy would conflict. User clarified
   the hostname is `tcb.jackylenghia.com` and explicitly reserved SSH-secret setup for themselves.
   Added separate production Compose, preserve-only secret bootstrap, deployment backup/migration/
   readiness script and manual CD with four user-managed secrets. SSH Git is JackyLN; GitHub CLI
   account jackyln1203 has READ only. Do not claim hosted CD execution without an actual run.
   Public deployment, certificate and existing-site regression results are in verification.md.

   Actual deployment correction: a manually mistyped full image SHA in the first invocation was
   caught; reran the same deployment script using `git rev-parse HEAD` directly. The accepted image
   and .deployed-sha now match 31018ede59dcfd00701eb21471f60ab546be5140. No reset occurred;
   generated account credentials were byte-for-byte preserved across the rerun. Hosted CI passed.


10. User asked which small GPT model would be intelligent enough for this demo, then requested:
    “add this decision in the document, too”. Checked official OpenAI model/API documentation in
    the preceding recommendation and inspected the existing Chat Completions adapter. Recorded
    GPT-5.4 mini snapshot gpt-5.4-mini-2026-03-17 in ADR 004, with dated rate assumptions and a
    planned max_completion_tokens/reasoning_effort=none request update. README, PLAN and evaluation
    guidance distinguish accepted selection from unimplemented adapter changes and unmeasured
    live results. Documentation consistency and whitespace were checked; no automated tests,
    Docker smoke, paid inference, key changes or deployment were run for this documentation-only edit.


Deployment maintenance follow-up (2026-11-08): user supplied Node.js 20 deprecation warnings from
CD run 42421131938. Inspected the run: both jobs succeeded, so the messages were warnings rather
than a deployment failure. Verified official checkout v7.0.1/setup-uv v10.3.3 action manifests use
Node.js 24 and replaced all old references in CI/CD with exact release commit pins. Kept the uv
CLI version and deployment/application commands intact. Validation outcomes are recorded in
verification.md. No API keys, SSH secrets or production environment values were inspected/changed.

Node.js 24 follow-up outcome: local actionlint/Ruff/28 tests passed, and hosted CI run 42421513904
passed the full Docker smoke/eval/DB checks with the new exact action pins. Completed annotations
were inspected: no Node.js 20 warning. CD was updated but not redispatched; the original reported
CD run was already successful. Only workflow/docs changed, with no production restart.

Public documentation follow-up (2026-11-08): user requested public Markdown reading, Mermaid and
section/subdocument navigation. Reviewed the existing documents and created a deliberately public
22-page subset, leaving deployment runbooks and credentials outside the published root. Selected
markdown-it-py/plugins/Pygments plus a locally bundled, strict-mode Mermaid renderer and added an
anonymous FastAPI reader, dynamic nested catalog, title search, TOC, previous/next navigation and
login/sidebar entry points. Mermaid is lazy-loaded so ordinary pages avoid diagram engine cost.
API/security/link-integrity tests and browser checks cover anonymous reading and rich Markdown.
The first local operations smoke expected SIMULATED AI but the user's local configuration now has
a live provider: it produced LIVE_FAILED_FALLBACK and the smoke assertion stopped. That is not a
successful offline smoke or a model evaluation. Regression is rerun against an isolated no-key
Docker database/app/worker; no environment values or credentials are copied into public docs.
Exact outcomes, including the isolated QA setup correction, are recorded in verification.md.

Public reader outcome: local lint/45 tests/publication check and anonymous desktop/mobile browser
checks passed. The isolated no-key full workflow smoke passed, and its disposable stack was removed.
Deployed source a489abeea12a3edd4dfd4557139e7e20c600f675; all 22 HTTPS documents and read-only browser
checks passed. No production investigations were triggered. See verification.md for exact scope.
Hosted CI 42424030055 also passed the fresh no-key Docker workflow, offline evaluation and DB checks.

Recorded live demo follow-up (2026-11-08): user authorized deployed credentials/key for one flow,
then asked to record the actions as a video. Inspected the configured model (key presence only)
and found ADR 004's adapter work still pending. Official OpenAI model/reference pages confirm
completion-token cap and none reasoning support. Implemented the bounded request update and
mocked tests before triggering a provider call. Added explicit-opt-in Playwright recording with
annotations and login via a non-recorded credential submission. Results remain pending.

Recorded demo outcome: first capture failed before any AI queue because HTMX replaced its caption
DOM node; fixed caption recreation and restarted. One subsequent live investigation succeeded.
Case #1/investigation #2 returned LIVE with four tools/two requests; 1,779 input/458 output tokens,
7,608 ms summed HTTP latency, estimated USD 0.00339525. Analyst #1 and supervisor #2 escalated
for independent evidence. The 87-second recording was converted to MP4 and sampled visually.
No claim of graded model accuracy follows from this observation. Exact checks in verification.md.

Public video publishing follow-up (2026-11-08): user asked to include the video README in docs.
Reused the reviewed existing 87-second recording, copied its chapters/outcome/usage into a public
product page, versioned the 1.9 MB MP4 and linked handbook/product/evaluation/README entries.
Added a constrained local-only video fence instead of enabling raw Markdown HTML. Extended tests
for rejected remote/nonvideo/missing sources and range downloads; browser checks cover playback,
seeking and mobile fit. No new model call or re-recording is needed. Results pending below.
Local public-video outcome: 51 tests/lint, all 23 pages/link validation, JS checks, Docker health
and anonymous browser checks passed. Video played and sought to the live-result frame; desktop
and mobile screenshots reviewed. Publication reuses the existing MP4; no new inference.
Public video deployment/browser checks passed, including seeking, mobile fit and byte-identical
MP4 verification over HTTPS. Public page: /docs/product/recorded-demo/. No new model calls.
Hosted CI 42425952741 passed lint/51 tests, 23-page validation and fresh Docker offline workflow/eval/DB checks.

Graded holdout follow-up (2026-11-08): user explicitly requested the outstanding 48-case real
provider evaluation and reviewer-visible failure explanations, then authorized production work
and local synchronization. Inspected PLAN section 6/B2 and the existing raw-JSON dashboard.
Implemented frozen dataset/prompt metadata, per-case checkpoints, exact-label/abstention grading,
scoped usage IDs and a readable dashboard/export. Transport/invalid responses now retain bounded
usage diagnostics. Expected labels are never added to model tool inputs. No prompt or fixture
change is made to optimize this holdout. Paid execution remains pending checks/deployment.

Actual production holdout outcome: source cc3c2e1c1fafbefa3fda3218201d4d1e65ff86a0 ran all
48 cases once, with no paid retry or post-observation prompt tuning. Score 18/48 (37.5%), valid
47/48; 29 accepted wrong labels and one rejected evidence_id prefix. No provider failure or
unknown usage. 96 requests, 82,342 input/20,290 output tokens; estimated USD 0.15306150.
Failure review found unsupported same-day rules, missed fee/net arithmetic, duplicate-credit
ambiguity and missing abstention. These are AI-assisted qualitative observations, not blinded
semantic grading. Preserved all failures, synced snapshot/progress locally, independently
checked fixture/count/Decimal-cost integrity and imported into local demo without inference.
Local browser initially found mobile table overflow; constrained grid tracks/min-width, then
read-only desktop/mobile/export checks passed with all 30 failures visible.
Final outcome: production authenticated dashboard/export and public report/JSON/progress passed
HTTPS desktop/mobile checks. Public snapshot matches original bytes; local repeat import reused
evaluation #3. Hosted CI 42429726168 passed 59 tests, 24-page validation and fresh Docker offline
workflow/DB checks. Live 37.5% remains plainly distinct from passing software/offline tests.

Controlled AI Investigation v2 milestone (2026-11-08): user requested inspection first, stronger
deterministic facts, consistency checks, maker-checker review, fresh separate benchmarks and
public documentation, explicitly withholding expensive bulk inference authorization. Reported
existing pipeline/37.5% history before changes; implemented pure evidence assessment, a closed
typed-claim/canonical-summary/catalog-hypothesis contract and versioned worker envelope. Failed
outputs remain original, flagged and blocked from approval. Read current state under consistent
review lock order; pending/failed/mandatory-escalation records cannot be approved. Legacy rows
and raw SYSTEM/dataset/report artifacts are unchanged (hash regressions).

Built controlled-synthetic-v2.0: 120 seeded cases, 48 development/72 holdout, independent expected
rubrics outside tools. Stable policy IDs identify immutable rate profiles; no model sees rubric
keys. Added scoped grading/support/abstention/escalation/latency/cost counters with explicit
unassessed denominators, and preserved raw track. A closed catalog was chosen instead of
claiming reliable semantic validation of unrestricted prose; live usefulness remains unmeasured.

Actual local checks: Ruff/83 tests, 26-page publication and JS/actionlint passed; no-key disposable
Docker migration/seed/HTTP flow/replay/independent approval/kill/retry passed; PostgreSQL competing
supervisor decisions committed once and audit/hash guards passed. Controlled offline 72/72
contracts and reference outcomes, zero provider calls. Desktop/mobile controlled-case/dashboard
and docs/Mermaid/video browser checks passed. Initial scripted fixtures use no model and cannot
be reported as AI accuracy. No paid v2 call or historical benchmark rerun was performed.

Deployment observation: source 16f3ee433d5a434d4526f792ce43a1b90baa7989 deployed with the existing
backup/migrate/seed-preserving workflow. Production offline Evaluation #3 ran with LLM_API_KEY
explicitly blanked: 72 scripted contracts/reference outcomes, zero requests/tokens/cost. Full
synthetic snapshot synchronized locally and imported as #4, without inference. Read-only HTTPS
v2/raw dashboard and public docs/video/Mermaid browser checks passed. Historical #2 JSON hash
and Payment/Payout/BankCredit/Match/ImportBatch counts matched the pre-deployment snapshot.
No new paid AI evaluation or financial decision was executed in production.

Final verification: runtime/public documentation source
`6f4b940bb6cc71f7bee6deb43fb7024bc51e498b` deployed healthy.
CI [42447744341](https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42447744341)
passed Ruff, 83 tests, 26-page link validation, fresh Docker migration/seed/smoke,
raw/offline-v2 harnesses and PostgreSQL concurrent-decision/audit checks.
Final production read-only v2/raw dashboard and anonymous source-pinned summary/Mermaid/mobile
checks passed; historical public result/log download hashes are unchanged. Local snapshot import
was repeated and returned the same Evaluation #4. Disposable no-key QA volumes were removed;
production/local application volumes were retained. No live v2 inference was performed.

## Live v2 evaluation preparation · 2026-11-08

Actual user instruction: measure live controlled-v2 quality, audit label isolation, first obtain
paid pilot approval, then seek separate holdout authorization. No paid response has been requested.
Inspection found correct v2 profile selection, but unconditional holdout selection, no operator
cost reservation and grouped failure handling that lost non-JSON model text. Added development
selection, frozen-hash checks, per-request conservative reservation cap, retained raw text/received
messages and explicit error categories, plus a no-repeat full-holdout guard. Prompt, dataset,
financial computation and historical artifacts were not changed. Mock HTTP tests examine actual
provider request bodies for grading containers and preserve malformed/unsafe output and usage.
Reflection: CLI --live alone is not the user's authorization; obtain explicit approval for the
proposed 12-case/USD 2 pilot, report failures honestly, then stop for holdout review/authorization.

Actual preparation verification: `make lint test docs-check` passed 92 tests, Ruff and 26 pages
(one pre-existing Starlette/httpx deprecation warning). Isolated no-key Docker CLI checks passed
72 holdout/12 development contracts with zero requests/model scores. HTTP smoke passed import,
replay, simulated investigation, independent approval, kill switch/retry and 14 screens; PostgreSQL
competing decisions/audit protections passed. Historical four-file hashes matched. Pilot selection
was staggered before any paid call to cover both payout currencies and six injected/six plain cases.

Live-evaluation preparation acceptance: source d3a1dd909d1661bf00373f1d770811707fc59660
deployed healthy; CI 42450227897 passed (92 tests, fresh Docker/offline and PostgreSQL checks).
Read-only HTTPS dashboard/raw export and anonymous pending-approval protocol/Mermaid/mobile checks
passed. Historical Evaluation #2 canonical JSON and five financial-table counts are unchanged.
Disposable QA stack/volumes removed. No paid evaluation or production financial decision was
executed. Await explicit 12-case/USD 2 pilot approval; frozen live holdout is not authorized.

## Workspace navigation polish · 2026-11-08

Actual user request: group the flat sidebar so banking work is distinct from administration and
resources. Follow-up constraint: do not commit or push until instructed. Inspected the existing
15 links, charcoal/red brand tokens and flat mobile scroll strip; captured desktop/mobile before
screenshots. Reused existing Jinja/CSS with a shared grouped navigation partial for desktop and
native mobile disclosure, preserving labels, URLs and server permissions. Included active-parent
highlighting for nested pages. No framework/dependency, backend financial or AI changes.
`make lint test docs-check` passed Ruff, 92 tests and 26-page link validation; one existing
Starlette/httpx deprecation warning. Local Docker app rebuilt/restarted healthy. No paid inference,
production deployment, commit or push performed. Browser verification observations follow below.

Browser observation/correction: first 320px check found existing fixed-width latest-run columns
and timestamps overflowing the page. Made mobile columns flexible and long run text wrap, then
rebuilt/rechecked. `node artifacts/navigation-polish-browser.mjs` passed four groups/all 15 routes,
nested active selection, desktop/short viewport, 320/390px layouts, keyboard/no-JS disclosure and
worker-health navigation. Screenshots before/after saved privately under artifacts and inspected.
No new persistent test suite was added for this presentation-only change. All edits remain local,
uncommitted/unpushed; production remains on its previous source and no model calls were made.

After local review, the user explicitly authorized committing and pushing the navigation polish
to main. The earlier local-only approval boundary is satisfied. This instruction does not request
a production deployment or authorize paid AI evaluation.

## Authorized production pilot and updated video · 2026-11-08

Actual user instruction: go ahead on production, store outcomes back in docs and add a new
section on the existing recorded-demo page. Interpreted as authorization for the proposed
12-case/USD 2 development pilot and production results recording/publication; no 72-case holdout.
Ran the existing frozen v2 command once: all 12 accepted with 72/72 typed claims supported,
2/2 abstentions and 4/4 escalations. No observed failure to fabricate or repair. Saved raw JSON,
progress and scoped request snapshot locally; imported as #5. Independently recounted 24 requests,
44798/4722 tokens, Decimal USD 0.05484750 and latency ranks 2869/6299 ms. All reported models
matched the snapshot; four tools per case; all final responses stopped normally. Historical
Evaluation #2 canonical JSON and financial table counts matched pre-run. Reviewed each report,
including missing gross, stale-rule conflict and simultaneous discrepancies; LATE_CREDIT for an
early credit remains a vocabulary limitation, not silently relabeled.

Recording approach: a read-only browser walkthrough of persisted results on production after
the CLI pilot completed. No additional model job or human decision is queued during filming;
login secrets are submitted outside the recorded DOM, only captions are injected. The original
87-second workflow video remains intact. No expert-human grading/productivity claim is invented.

Recording correction: the first read-only capture stopped after the historical benchmark because
an HTMX body replacement removed the injected caption. No paid inference or decision was repeated.
Restored the caption recreation behavior already used in the older recorder and reran a fresh
continuous read-only capture; the incomplete first capture remains private as diagnostic evidence.
Independent integer-only fee/net recount also passed for every complete pilot fixture; missing
gross was skipped as unknown rather than filled with a value.

Final observed acceptance: source adcb3c8fcbabc914b47052442f7cbaf9d7ed4ed6 deployed healthy,
CI 42474078101 passed (92 tests, clean Docker/offline workflow and PostgreSQL checks).
`DOCS_BASE_URL=https://tcb.jackylenghia.com npm run docs:browser`, `npm run eval:browser`,
and explicit offline `v2:browser` passed. Additional read-only browser checks verified public
pilot report/JSON and new MP4 hashes/ranges, live #4 metrics, desktop/mobile layout and no page
errors. Old raw #2 canonical JSON/financial-table counts are unchanged after publishing.
Production has exactly one V2_LIVE evaluation and zero provider requests after pilot completion.
Original paid responses are locally imported as #5; the video adds no provider spend.
The 72-case live holdout remains unrun and requires a separate approval after review.
