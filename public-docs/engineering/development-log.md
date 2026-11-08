# AI-assisted development log

These are excerpts from actual project requests and observed corrections. They are not stakeholder
interviews or a fabricated series of prompts. Operational access details and credential material
are omitted from this public record.

## Important requests and resulting work

| Actual request | Implementation response and evidence boundary |
| --- | --- |
| “follow CODEX_MASTER_PROMPT.md and setup the project as instruct” | Built the Python application, deterministic settlement flow, durable jobs, roles, approvals and tests. Preserved the synthetic-only boundary. |
| “regarding the UI, refering techcombank branding color to re-update the UI” | Updated the shared palette to red, charcoal, white and grey, with restrained gold. Adapted action reds for text contrast instead of claiming exact brand compliance. |
| “alright, let's do code deployment” | Added a shared-proxy production target and a repeatable backup/migration/readiness deployment path. Verified public HTTPS and the existing applications' protected responses. |
| “add this decision in the document, too” | Recorded the small-model choice, version pin, dated pricing assumptions and pending integration/live evaluation in ADR 004. Selection is not a measured quality result. |
| “consider updating the deployment, due to this error” | Inspected the supplied Actions run: it succeeded with Node.js deprecation warnings. Updated action runtimes to Node.js 24 and verified a subsequent hosted CI run. |
| “Create a public docs in codebase” | Added this curated public Markdown tree and reader, rich Markdown, Mermaid and nested navigation. Kept internal runbooks and generated credentials outside the public source. |

## Actual failures and corrections

- Initial pytest discovery could not import the application package; the test configuration gained
  an explicit repository Python path, and tests were rerun.
- A draft migration depended on mutable ORM metadata; it was replaced with explicit migration code.
- Browser verification caught a JavaScript syntax error and an inline-style CSP problem that API
  tests missed. Both were corrected and browser checks added.
- A narrow-screen chart resize issue required a dedicated responsive container and a bounds check.
- The audit chain could use a stale cached head in an existing session; refreshing after locking
  and a regression test protected chain continuity.
- A smoke fixture assumed simulated AI while a local provider was configured. The assertion stopped
  on fallback output; baseline regression was moved to an isolated no-key Docker environment.

## Reflection and limits

Deterministic database behavior and explicit labels provide more credible evidence than invented
model scores. API tests alone do not prove browser rendering. Citation membership does not prove
semantic support, and synthetic cases do not establish bank-domain safety.

Live model quality, calibrated confidence, real stakeholder discovery and production banking
assurance remain outstanding. Read the [evaluation limits](../ai/evaluation.md),
[security boundary](security.md) and [model decision](decisions/004-demo-llm-selection.md)
when assessing what the prototype demonstrates.


## Actual follow-up: recorded live flow

The user authorized the deployed key for one synthetic flow and asked to record actions as a video.
We found the selected model's request contract was still pending, verified official documentation,
implemented completion-token/none-reasoning options and tested with mocked HTTP before deploying.
The first capture stopped before any AI job because HTMX replaced the annotation element; corrected
the recorder, then queued one investigation. It returned LIVE with four evidence tools. A separate
supervisor escalated for missing independent provider proof. The 87-second actual browser recording
contains explanatory captions. One successful workflow is not a model-accuracy benchmark; see
the [evaluation observation](../ai/evaluation.md#observed-single-live-demonstration).

## Live controlled-v2 development pilot and updated recording

The authorized 12-case production pilot accepted 12/12 with 72/72 supported typed claims,
2/2 required abstentions and 4/4 escalations. No failure was observed; estimated model cost was
USD 0.05484750. The [complete measured report](../ai/controlled-v2-pilot-2026-11-08.md) publishes
all original responses, every inspected scenario and the limits of this rule-guided score.
The scoped snapshot was synchronized locally without changing finance records; raw-v1 is preserved.
A [new results walkthrough](../product/recorded-demo.md#controlled-v2-results-walkthrough) reviews
persisted production evidence without additional inference. The first read-only capture hit an
HTMX caption-removal issue; the handler was corrected for the completed continuous recording.
The 72-case live holdout still requires separate authorization.
