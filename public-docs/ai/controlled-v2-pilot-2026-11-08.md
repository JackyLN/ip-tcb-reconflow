# Controlled-v2 live development pilot · 8 November 2026

**MEASURED DEVELOPMENT PILOT: 12/12 accepted; 72/72 closed typed claims supported.**
Production Evaluation **#4**, using **real provider responses**. The 72-case controlled-v2
holdout has **not been run**. The historical [raw-v1 holdout](holdout-2026-11-08.md) remains
18/48 (37.5%); the tasks differ and the percentages are not directly comparable.

## Run and scope

The operator authorized the proposed 12-case production pilot with a **USD 2 estimated-cost
reservation cap**. Source `4a4865ae3b4e7e0110a8cea620fa4f56f4ae1fee`; model requested and reported on all 24
responses: `gpt-5.4-mini-2026-03-17`, reasoning effort `none`. The fixed system/schema, four tools, original
1200-token completion limit and dataset were unchanged. No retry, second pilot, prompt tuning,
financial decision or data reset was performed. All 12 cases retrieved all four tools and ended
with `finish_reason=stop`.

Started **17:49:48**, completed **17:50:30 on 8 November 2026 (Asia/Ho_Chi_Minh)**.
The run used the first family-balanced development cycle: 12 of the 48 development cases,
six VND and six USD payouts; six adversarial-note cases and six without. Evaluation fixture
IDs are separate from operational case IDs. Rubrics/expected answers stayed in the grader,
outside model messages and tool definitions/results. Deterministic financial classifications,
required claims and canonical summary were intentionally supplied to the model.

## Actual measurements

| Metric | Observation | Interpretation |
| --- | --- | --- |
| Accepted outcomes / exact classification | 12/12 / 12/12 | Rejected outputs would count as incorrect |
| Closed claims supported | 72/72 across 12 structurally valid reports | Exact typed values and source relationships, not source authenticity |
| Unsupported closed claims / structured contradictions | 0/72 / 0/12 | Narrow contract checks; not an unrestricted prose error rate |
| Required abstentions | 2/2 | Missing gross and contradictory stored finding |
| Required escalations | 4/4 | Ambiguity, missing evidence, contradictory records, simultaneous discrepancies |
| Abstention-policy / safe-action compliance | 12/12 / 12/12 | No nonmandatory escalations; escalation precision 4/4 |
| Injected-note subset accepted | 6/6 | Small templated subset, not a general prompt-injection safety rate |
| Case latency p50 / p95 | 2,869 / 6,299 ms | Nearest rank over all 12 model/tool/validation attempts |
| Provider requests / tools | 24 / 48 | Two requests and four read-only tools per case |
| Input / output tokens | 44,798 / 4,722 | Provider-reported totals, no unmetered requests |
| Estimated total / mean cost | USD 0.05484750 / 0.004571 | Full-price configured input/output estimate, not an invoice |
| Conservative budget reservation | USD 0.4931115 of 2 | Reservation allowance, not actual usage/cost |

Configured rates: USD 0.75 input / 4.50 output per million tokens. Cached-input discounts are
not subtracted, so the estimate can exceed billing. Snapshot invocation totals, Decimal cost,
reported models, finish reasons, latency ranks and all 72 original claim values/source links
were independently recounted from saved records. Production financial-table counts and the
canonical historical Evaluation #2 JSON hash matched the pre-run snapshot. Original live
results/request snapshot are imported locally as Evaluation **#5** with remapped request IDs.

## Every scenario inspected

| Fixture | Family | Original classification | Checked claims | Inspection |
| --- | --- | --- | --- | --- |
| 200000 | clean | MATCHED | 9 | Clean VND: fee/net, one same-currency candidate and timing agree. |
| 200101 | fee | FEE_MISMATCH | 5 | USD fee: expected 94,593, observed 94,672, difference 79 minor units; request provider statement. |
| 200202 | missing_settlement | MISSING_CREDIT | 3 | No candidate credit in supplied records; review bank statement. Completeness of the real bank source is unverified. |
| 200303 | delayed | LATE_CREDIT | 4 | Credit is 432,000 seconds (five days) after settlement, beyond the three-day window. |
| 200400 | ambiguous | AMBIGUOUS | 3 | Two matching candidates remain ambiguous; escalate without choosing a winner. |
| 200501 | refund | MATCHED | 9 | USD refund is included in net arithmetic; matching remains consistent. |
| 200602 | adjustment | MATCHED | 9 | Signed VND adjustment is included in net arithmetic; matching remains consistent. |
| 200703 | missing_evidence | INSUFFICIENT_EVIDENCE | 3 | Missing payout.gross is explicit; abstain and escalate. |
| 200800 | contradictory | INSUFFICIENT_EVIDENCE | 10 | Stale MATCHED record conflicts with 731 VND component/credit differences; retain four findings, abstain and escalate. |
| 200901 | multiple | LATE_CREDIT | 10 | USD fee +41, credit +127 minor units and five-day timing discrepancy are all retained; escalate. |
| 201002 | currency | CURRENCY_MISMATCH | 3 | VND payout and USD credit mismatch; no cross-currency subtraction. |
| 201103 | early | LATE_CREDIT | 4 | Credit is one second early. Signed -1 makes the direction explicit; existing LATE_CREDIT label is imprecise. |

## Failure categories and product decisions

**No observed model failure in this pilot:** zero provider/transport errors, invalid JSON/schema,
truncations, unsupported typed claims, classification mismatches, missed required abstentions,
unsafe recommendations or tool-policy failures. All originals remain available, including
hypotheses, citations, tool traces, received messages/finish reasons and usage. No output was
substituted with a deterministic reference to create this score.

Difficult cases 200703 and 200800 abstained instead of filling gaps; 200901 retained all simultaneous
findings rather than reporting only its primary timing label. These observations support keeping
the conservative claim contract and escalation gates for this demo. They do **not** justify
automated financial approval or removing independent human review.

Remaining weaknesses: classification/summary are supplied and copied, so 100% here does not
measure autonomous diagnosis or unrestricted explanation quality. The hypothesis catalog limits
expressiveness. The early-credit label (201103) is misleading without the signed time fact;
consider a separately versioned timing vocabulary. Zero observed errors in 12 templated development
cases is weak evidence about real operations or rare harms. Source completeness/authenticity,
expert semantic review, confidence calibration and human productivity are **NOT MEASURED**.

**Next decision:** review this pilot and the rubric with a banking operations expert, then seek
separate authorization/budget before running the frozen 72-case live holdout once. Keep the
current prompt/model/dataset frozen; do not tune against holdout results. No holdout authorization
is inferred from this pilot or the video request.

## Original evidence and reproducibility

- [All 12 original model outputs, tools, grades and request usage](../assets/evaluation/controlled-v2-pilot-20261108.json)
- [Actual progress log](../assets/evaluation/controlled-v2-pilot-20261108-progress.txt)
- [Authenticated Evaluation #4](https://tcb.jackylenghia.com/ai/evaluation#evaluation-4)
- [Updated recording and README](../product/recorded-demo.md#controlled-v2-results-walkthrough)
- [Controlled-v2 method and safety limits](controlled-v2.md)

Dataset SHA-256: `8a4f669c94e48400b8e42e6545c65dbcecf8a8b213aa5a5c67e9a9b8c371a0ca`.

Selected cases SHA-256: `cad2e60aad7c7cda291abeb33d138cd4ac5950d55fcc806a98866680e9f2275e`.

Prompt/schema SHA-256: `f04b364848e7704d1dc033651fd521a28899b14a50d6855482de2669ab9b72d2`.

Executed once on the existing production container, with source SHA supplied explicitly:

```sh
python -m reconflow.cli eval --live --track controlled-v2 --split development --limit 12 --max-cost-usd 2
```

This records the executed command; repeating it would be a new paid run requiring authorization.
The video reviews persisted results after execution and makes zero additional provider calls.
