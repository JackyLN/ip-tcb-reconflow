# Evaluation and AI limits

## Selected model and validation status

[ADR 004](adr/004-demo-llm-selection.md) selects GPT-5.4 mini snapshot
`gpt-5.4-mini-2026-03-17` for the demo, with initial request `reasoning_effort: none`.
Selection and the adapter request contract are **IMPLEMENTED**. Requests use
`max_completion_tokens`; GPT-5.4 mini explicitly uses `reasoning_effort=none`. Mocked HTTP tests
verify this contract without a paid key. A single authorized recorded live demonstration
succeeded. The subsequent 48-case live holdout scored **18/48 (37.5%)**;
semantic hallucination/safety rates remain **NOT MEASURED**.

## Existing evaluation workflow

Dataset synthetic-v1: 72 deterministic cases, 24 development / 48 holdout; eight root-cause
categories, including insufficient evidence, contradictions (payout arithmetic), currency,
duplicates and adversarial notes. Expected labels are absent from live tool input. Rule findings
are available to normal in-app investigations because AI explains the deterministic finding.
Evaluation fixtures are deliberately separate and omit those rule findings.

`make eval` runs SIMULATED_CONTRACT_CHECK: validates schema and evidence membership for scripted
outputs and scores the deterministic fixture baseline. It never calls a provider and never reports
a model classification score. This does not measure live accuracy or prompt-injection resistance.

Explicit paid full holdout command: `docker compose run --rm app python -m reconflow.cli eval --live --limit 48`.
Set LLM_API_KEY, LLM_MODEL, LLM_BASE_URL and operator-verified USD input/output prices per million.
The OpenAI-compatible adapter uses /chat/completions, four allowlisted tools, <=5 HTTP calls,
<=1200 completion tokens each, 10s HTTP timeout and a time check before each request. HTTP phase
timeouts are not a strict wall-clock kill. Tool outputs are small aggregates and <=10 credits.
No model SDK or proprietary matching logic is required. No live calls occur implicitly in tests.
Once credentials are configured, clicking investigate explicitly queues live inference.

Live runs store confusion counts, individual failures, schema/citation validity, abstention count,
latency p50/p95; HTTP invocations record actual usage and estimated cost from configured prices.
Unknown provider usage and zero price rates must not be interpreted as free inference.
NOT MEASURED: calibrated confidence, semantic hallucination rate, high-risk escalation recall,
blinded abstention quality, real-bank accuracy and controlled AI versus human workflow benefit.
Review failed reports manually; citation membership alone cannot prove a statement is supported.

Limits: compatibility was observed for the selected model in one demo; this does not establish quality. A worker crash after
an external call can cause a repeated paid call; DB effects remain idempotent. Job retry max three
bounds this risk, but external model calls are not exactly-once. No automatic model report can
create a proposal or resolve a case. A live failure produces LIVE_FAILED_FALLBACK and human review.


## Observed single live demonstration · 2026-11-08

**MEASURED workflow observation, not a graded evaluation:** synthetic 1,000-payment mismatch
source replayed; case #1, investigation #2 returned LIVE using gpt-5.4-mini-2026-03-17. Four
read-only evidence tools and two provider requests; 1,779 input and 458 output tokens; summed
request latency 7,608 ms. **ESTIMATED** cost USD 0.00339525 using configured rates, not an invoice.
The report identified a 100 USD-minor-unit fee difference (USD 1), cited observed evidence and
requested a provider statement. Its self-reported high confidence remains **UNCALIBRATED**.
An analyst proposed escalation; a separate supervisor escalated the unresolved case. No financial
records changed. The actual browser flow was recorded with explanatory captions. One successful
request sequence does not establish semantic accuracy, safety rates or general latency/cost.


## Graded holdout method

The explicit live runner freezes synthetic-v1 (72 total, 24 development/48 holdout, six holdout
variants for each of eight labels) and the investigator-v1 prompt using SHA-256. Expected labels
and grading reasons are not supplied to model tools. This is a small templated set sharing
patterns with development, with no clean MATCHED examples or broad refund/mixed-error coverage.
It is not an independent sample of real bank exceptions.

Exact-label accuracy includes invalid reports and provider errors as incorrect. Also report
42 determinable-label cases separately, macro F1, abstention precision/recall, confusion counts,
schema/evidence acceptance and adversarial-note classification counts. Evidence membership is
not semantic support. High-risk recall and unsupported-claim rate remain NOT MEASURED.
Per-case latency includes all model/tool HTTP turns and validation; p50/p95 use nearest rank over
all attempted cases. Provider token usage and configured-price estimates are scoped to the run,
with unknown/unmetered requests visible rather than declared free. There are no automatic case
retries. The admin kill switch is checked before each case.

The CLI checkpoints each completed case, its report/trace/reference evidence and request IDs.
An interrupted run stays RUNNING with the completed prefix; it is not a completed 48-case score.
An in-flight provider call may be charged without a saved response if its process is killed.
The signed-in evaluation dashboard provides scores, all failures and a JSON download.
The user-authorized production run completed: 18/48 correct, 47/48 schema/citation-valid,
30 failures, p50/p95 3,369/4,582 ms, estimated USD 0.15306150.

See the [full measured holdout report and all failure cases](holdout-2026-11-08.md),
including the downloadable synthetic JSON and original progress log.

## Controlled Investigation v2

See [the public v2 method/status](../public-docs/ai/controlled-v2.md) and ADR 005.
`make eval-v2` runs a 72-case offline harness with zero provider requests; it does not replace
raw-v1 or measure live AI accuracy. Live v2 metrics require separate explicit authorization.

## Live v2 preparation audit · 2026-11-08

**PREPARED; PAID RUNS NOT AUTHORIZED OR EXECUTED.** Live v2 selects
`controlled.SYSTEM_V2` plus `ControlledReport.model_json_schema()`, the original four scoped
read-only tools, JSON mode, `reasoning_effort=none` for the configured snapshot, and the existing
five-request/four-tool/1200-completion-token limits. Runtime model/key configuration was inspected
without printing secrets or calling the provider: `gpt-5.4-mini-2026-03-17`, OpenAI endpoint,
configured input/output USD 0.75/4.50 per million. These agree with the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini).

Frozen dataset SHA256 remains
`8a4f669c94e48400b8e42e6545c65dbcecf8a8b213aa5a5c67e9a9b8c371a0ca`;
prompt/schema SHA256 remains
`f04b364848e7704d1dc033651fd521a28899b14a50d6855482de2669ab9b72d2`.
The runner now rejects changes to either. Holdout order is unchanged. Development selection
cycles 12 families before choosing another variant, so a 12-case pilot covers every family
using staggered development variants: six VND and six USD payouts, six with adversarial notes
and six without. Selection IDs/digest and
split are saved separately from the full dataset fingerprint.

Input boundary: only `case['tools']` is enriched and passed to the adapter. The outer `expected`,
`family`, and `split` values are retained by the grader; adapter messages contain the system
contract, synthetic exception ID and observed tool results. The model has no filesystem, SQL,
HTTP or rubric retrieval tool. Mock HTTP tests inspect actual serialized bodies recursively.
Computed deterministic classifications and required claims ARE deliberately supplied; this is
rule-compliance evaluation, not independent diagnosis or a claim that answers are unknowable.
This is process isolation, not a cryptographic guarantee against a changed implementation.

Live v2 now requires an explicit positive `--max-cost-usd`. Before every HTTP request, the runner
reserves a deliberately conservative configured-rate estimate: twice the serialized JSON byte
count plus 4096 input framing tokens, and all 1200 possible output tokens. Reservations are never
recycled after errors. This is an application estimate, not an invoice guarantee or provider-side
project spending limit. The run stops before a request exceeding that estimate; unknown request
usage stops further cases. No automatic retries or resumptions are performed. Budget denial
before a case's first request is not counted as a model attempt.

Malformed JSON text, original parsed reports and every received model message/finish reason,
reported model and usage are retained. HTTP/transport errors, invalid provider responses, invalid
JSON, truncation, tool-policy failure and consistency flags remain distinct. Classification
mismatches and unsafe actions are additionally categorized even when a report fails schema.
Schema-invalid claims remain unassessed. Metrics use all attempted cases; incomplete runs are
not completed holdout scores. Cost uses uncached input rates and can overestimate cached input;
unknown usage can omit charges. Response usage and `finish_reason` semantics follow the
[official Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).

**PROPOSED pilot (requires operator approval):** 12 development cases, one per family, existing
snapshot/prompt, estimated-cost reservation cap USD 2, at most 60 HTTP requests/72000 completion
tokens, no retries. Stop on budget or unmetered usage. Review every failure and publish original
outputs/metrics. Only after pilot review, request separate authorization/budget for the frozen
72-case holdout. The runner refuses partial live holdout runs and any second live run of this
dataset, including after an interrupted run. Any future prompt/dataset tuning needs a separately
versioned protocol; do not tune against the holdout or relabel its failures.

## Authorized live v2 pilot outcome · 2026-11-08

Production Evaluation #4 completed 12 development cases once on source
4a4865ae3b4e7e0110a8cea620fa4f56f4ae1fee, with USD 2 estimated-cost cap. All 12 accepted,
72/72 supported typed claims, 2/2 required abstentions, 4/4 required escalations; no observed
provider/schema/claim/classification/unsafe-action failures. 24 requests, 44,798 input/4,722 output
tokens; estimated USD 0.05484750, p50/p95 2869/6299 ms. No retries/tuning, no live holdout run.
Full original responses/tool traces/grades and scoped invocation snapshot synchronized locally
as Evaluation #5. Historical raw-v1 #2 and financial-table counts stayed unchanged.
See [all twelve inspected scenarios, evidence, limitations and product decisions](../public-docs/ai/controlled-v2-pilot-2026-11-08.md).
This measures a closed rule-guided development contract, not autonomous diagnosis, real-bank
accuracy, independent source authenticity, semantic creativity or productivity. The 72-case live
holdout requires separate approval after pilot review.
