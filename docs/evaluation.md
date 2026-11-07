# Evaluation and AI limits

## Selected model and validation status

[ADR 004](adr/004-demo-llm-selection.md) selects GPT-5.4 mini snapshot
`gpt-5.4-mini-2026-03-17` for the demo, with initial request `reasoning_effort: none`.
Selection and the adapter request contract are **IMPLEMENTED**. Requests use
`max_completion_tokens`; GPT-5.4 mini explicitly uses `reasoning_effort=none`. Mocked HTTP tests
verify this contract without a paid key. A single authorized recorded live demonstration is
pending; graded holdout results remain **NOT MEASURED**.

## Existing evaluation workflow

Dataset synthetic-v1: 72 deterministic cases, 24 development / 48 holdout; eight root-cause
categories, including insufficient evidence, contradictions (payout arithmetic), currency,
duplicates and adversarial notes. Expected labels are absent from live tool input. Rule findings
are available to normal in-app investigations because AI explains the deterministic finding.
Evaluation fixtures are deliberately separate and omit those rule findings.

`make eval` runs SIMULATED_CONTRACT_CHECK: validates schema and evidence membership for scripted
outputs and scores the deterministic fixture baseline. It never calls a provider and never reports
a model classification score. This does not measure live accuracy or prompt-injection resistance.

Explicit paid live command: `docker compose run --rm app python -m reconflow.cli eval --live --limit 6`.
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

Limits: provider response compatibility is unverified without credentials. A worker crash after
an external call can cause a repeated paid call; DB effects remain idempotent. Job retry max three
bounds this risk, but external model calls are not exactly-once. No automatic model report can
create a proposal or resolve a case. A live failure produces LIVE_FAILED_FALLBACK and human review.
