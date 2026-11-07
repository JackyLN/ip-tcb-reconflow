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
