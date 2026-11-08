# Advisory AI

AI helps articulate contextual hypotheses and missing evidence after deterministic reconciliation
has already identified a discrepancy. It cannot decide financial truth or close a case.

## Scoped evidence tools

The investigator can retrieve a case, payout/payment/refund/fee aggregates, bounded candidate bank
credits and a provider policy. At most four tool calls and five provider requests are permitted in
an investigation. Per-request output limits, timeouts and daily job quotas bound resource use.

## Report contract

The server validates a report's schema, case ID and cited evidence membership. The report separates
confirmed facts, hypotheses, missing evidence, an advisory next step and an uncalibrated confidence
band. Human review is enforced independently of a model's suggested confidence.

| Mode | What it means |
| --- | --- |
| SIMULATED | Scripted no-key demonstration; no live model inference. |
| LIVE | Configured provider output accepted by the server's structural/evidence gates. |
| LIVE_FAILED_FALLBACK | Live availability or validation failed; human investigation remains necessary. |

## Selected model and measured limits

[ADR 004](../engineering/decisions/004-demo-llm-selection.md) records the accepted GPT-5.4 mini
snapshot and dated token-price assumptions. The adapter is implemented, and a real 48-case
holdout scored **18/48 (37.5%)**. This does not pass as a reliable authoritative classifier.

Read the [evaluation contract](evaluation.md) for the synthetic holdout split, actual offline
results, the [measured holdout and failure report](holdout-2026-11-08.md), and remaining semantic
grading gaps. Confidence remains
uncalibrated; there is no automatic financial approval in any mode.
