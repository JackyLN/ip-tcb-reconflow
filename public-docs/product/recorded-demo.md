# Recorded live demo

**New:** [Controlled-v2 results walkthrough](#controlled-v2-results-walkthrough) — 12-case live
development pilot, original outputs and the grouped workspace. The earlier workflow video below is preserved.

Recorded on **8 November 2026 (Asia/Ho_Chi_Minh)**. Actual browser actions with explanatory
captions, synthetic data and a live configured model. No narration or reconstructed actions.
Recording source: `6d44ecc98793b2de137f848722380091cf4d9593`.

## Watch the walkthrough

87 seconds · MP4/H.264 · approximately 1.9 MB · no account needed to watch.

```video
../assets/demo/reconflow-live-demo.mp4
```

[Open or download the MP4](../assets/demo/reconflow-live-demo.mp4).
The browser may open its own player; use the player menu to download.

The recording shows a **LIVE** investigation (#2) for [case #1](https://tcb.jackylenghia.com/exceptions/1).
The console case requires separate sign-in; watching this recording grants no console access.

## Outcome

1. Analyst replays the 1,000-payment mismatch scenario; the existing import/run is reused.
2. Payout #2 has an observed fee of USD 188.99 versus policy USD 187.99: a **USD 1 difference**.
3. GPT-5.4 mini reads four scoped evidence tools and requests independent provider confirmation.
4. The analyst proposes escalation; a separate supervisor escalates proposal #2.
5. Case #1 remains **ESCALATED**. Audit events record the distinct actors; no money moved.

The video is a dated observation of the shared demo, not a claim that its current totals or case
state will remain unchanged. Later demo activity can alter the console.

## Chapters

- 00:02 — 01 · Analyst workspace: Synthetic merchant settlements. The configured GPT model is advisory; no money can move.
- 00:06 — 02 · Load the scenario: 1,000 payments, grouped into payouts. Existing identical source data is safely reused.
- 00:10 — 03 · Deterministic reconciliation: Python calculates payout totals and compares bank credits. Replaying does not double-count.
- 00:14 — 04 · Inspect the findings: Matched, fee, timing, missing-credit and ambiguity findings come from rules, not the LLM.
- 00:19 — 05 · Read the payout evidence: Inspect currency, expected fee, declared net and candidate bank credit before drawing conclusions.
- 00:24 — 06 · Evidence before AI: Four scoped read-only tools expose the case, payout math, candidate credits and provider policy.
- 00:30 — 07 · Live GPT investigation: Waiting for the real provider response. One investigation; at most four tools and five API requests.
- 00:41 — 08 · Actual AI result: Provider result: LIVE. Citations are validated; semantic accuracy still needs human review.
- 00:49 — 09 · Inspect the tool trace: Only observed evidence IDs can be cited. The model cannot approve, write finance records or execute SQL.
- 00:55 — 10 · Human recommendation: The analyst proposes escalation for independent provider evidence; AI submits no resolution itself.
- 00:59 — 11 · Maker-checker boundary: The proposal is pending. The analyst cannot approve their own recommendation.
- 01:04 — 12 · Independent supervisor: A separate supervisor account reviews the analyst proposal. Login secrets were excluded from the recording.
- 01:08 — 13 · Review the recommendation: Evidence is insufficient for closure. Escalation preserves the unresolved discrepancy.
- 01:15 — 14 · Recorded outcome: Case escalated by an independent supervisor. No balances changed and no payment was executed.
- 01:20 — 15 · Audit trail: The real application records investigation, analyst proposal and supervisor escalation with distinct actors.

## Observed usage

| Observation | Value | Interpretation |
| --- | --- | --- |
| Model | `gpt-5.4-mini-2026-03-17` | Observed configured snapshot |
| Investigation mode | LIVE | Actual provider response, validated schema/citations |
| Provider requests / evidence tools | 2 / 4 | One queued investigation |
| Input / output tokens | 1,779 / 458 | Provider-reported usage |
| Summed HTTP request latency | 7,608 ms | Excludes queue, polling and browser pauses |
| Estimated provider cost | USD 0.00339525 | Configured token rates; not a provider invoice |

**MEASURED** values describe this one run. Cost is **ESTIMATED**. Graded holdout accuracy and
semantic claim support remain **NOT MEASURED**; the model's high confidence is **UNCALIBRATED**.

The analyst proposed escalation and a different supervisor escalated case #1. No finance records were adjusted. One demonstration does not measure model accuracy, calibration or production safety.

The initial capture failed before any AI job was queued because HTMX replaced the caption node; the corrected capture completed. MP4 is a format conversion of the continuous browser recording, with no reconstructed actions.


## Repeat the flow yourself

Use privately supplied analyst credentials: **Sources & imports → Mismatch → 1,000 → Launch
reconciliation**. Inspect a payout and its open exception, then queue a bounded AI investigation.
Submitting an evidence-based recommendation moves it to review. Sign in as a different supervisor
to approve, reject or escalate; insufficient independent evidence calls for escalation.

Queueing a new investigation uses the configured provider and can incur cost. Watching or
downloading this existing recording is read-only and makes no model call. See the
[workflow](workflow.md), [evaluation limits](../ai/evaluation.md) and [security boundary](../engineering/security.md).

The reproducible recording script is `scripts/record-demo.mjs` with explicit `RUN_LIVE_DEMO=1`
opt-in; private credentials are submitted outside the recorded DOM. They are never included here.

The later [48-case graded holdout](../ai/holdout-2026-11-08.md) scored 37.5%; this single
successful workflow recording is not evidence of general diagnostic accuracy.

## Controlled-v2 results walkthrough

Recorded on **8 November 2026 at 17:56 (Asia/Ho_Chi_Minh)** on the production site.
**3 minutes 8 seconds** · MP4/H.264 · approximately 3.4 MB · explanatory
on-screen captions, no narration · anonymous playback/download.

```video
../assets/demo/reconflow-controlled-v2-demo.mp4
```

[Open or download the updated MP4](../assets/demo/reconflow-controlled-v2-demo.mp4) ·
[Chapters, captions and recording metadata](../assets/demo/controlled-v2-demo-chapters.json) ·
[Complete measured pilot report](../ai/controlled-v2-pilot-2026-11-08.md) ·
[All original model outputs and evidence](../assets/evaluation/controlled-v2-pilot-20261108.json).

### What this recording demonstrates

Actual browser navigation on `tcb.jackylenghia.com`: the four workspace groups, synthetic intake,
payouts, deterministic financial evidence, saved live Evaluation #4, original fee/missing/conflict/
multi-discrepancy model reports, historical raw-v1 result, human review queue, audit trail and
worker health. The production runtime source was `4a4865ae3b4e7e0110a8cea620fa4f56f4ae1fee`.
Operational case #1 and evaluation fixture IDs are separate; the recording labels that distinction.

The **12-case paid development pilot completed before filming**. This recording reviews persisted
responses; it makes **zero additional provider calls**, submits no import/recommendation/approval
and changes no financial records. Login credentials were submitted outside the recorded DOM;
only explanatory captions were injected. The MP4 is a format conversion of one continuous browser
capture. The first read-only attempt stopped when HTMX removed a caption; the corrected continuous
recording is published here. No paid run was repeated to obtain the video.

### Observed pilot results

| Observation | Result | Interpretation |
| --- | --- | --- |
| Production / local record | Evaluation #4 / #5 | Full scoped snapshot synchronized locally, request IDs remapped |
| Model | `gpt-5.4-mini-2026-03-17` | Requested and provider-reported snapshot |
| Accepted outcomes | 12/12 | Small development sample, deterministic findings supplied |
| Typed claims supported | 72/72 | Closed values/source relationships; no source-authenticity guarantee |
| Required abstentions / escalations | 2/2 / 4/4 | Missing/contradictory evidence and risky ambiguous/multiple findings |
| Requests / input / output tokens | 24 / 44,798 / 4,722 | Provider-reported pilot usage; filming adds zero calls |
| Latency p50 / p95 | 2,869 / 6,299 ms | All pilot attempts, including tool/validation time |
| Estimated pilot cost | USD 0.05484750 | Configured full-price rates, not an invoice |
| Observed pilot failures | 0 | Does not establish a zero failure rate in real operations |

The historical raw-v1 score remains **18/48 (37.5%)**; its raw diagnosis task differs from v2's
rule-guided compliance task. **NOT MEASURED:** v2 live holdout/generalization, independent source
authenticity, unrestricted semantic factuality, calibration or human productivity improvement.
The 72-case live v2 holdout remains **NOT RUN**, pending separate approval after pilot review.

### New walkthrough chapters and transcript

- 00:02 — **01 · Production workspace**: The live pilot finished before this recording. This walkthrough reads actual saved results; it queues no AI jobs.
- 00:11 — **02 · Grouped navigation**: Banking operations, Reporting & assurance, Administration and Resources separate daily work from system tasks.
- 00:21 — **03 · Synthetic intake**: Only synthetic or public evidence belongs here. No import is submitted in this results walkthrough.
- 00:30 — **04 · Payouts, not one-to-one payments**: Payments are aggregated into payouts; Python integer arithmetic establishes financial findings.
- 00:40 — **05 · Financial evidence first**: This stored operational case shows fee, net, currency and timing checks. It is separate from synthetic evaluation fixture IDs.
- 00:51 — **06 · Actual controlled-v2 pilot**: 12/12 accepted; 72/72 closed claims supported. One development example per family; this is not a holdout score.
- 01:02 — **07 · Measured usage and latency**: 24 requests; 44798/4722 input/output tokens; p50/p95 2869/6299 ms. Estimated USD 0.05484750.
- 01:13 — **08 · No observed pilot failures**: No provider, schema, unsupported-claim or policy failure appeared in these 12 cases. This does not establish a zero production failure rate.
- 01:23 — **09 · Original fee report**: Fixture 200101: expected fee 94,593 USD minor units; observed 94,672; difference 79. The model cites payout and policy evidence.
- 01:34 — **10 · Missing evidence means abstain**: Fixture 200703 lacks payout.gross. The original model response says INSUFFICIENT_EVIDENCE, abstains and escalates.
- 01:46 — **11 · Conflicting records stay visible**: Fixture 200800 retains the stored-rule conflict and 731 VND difference. It abstains and escalates instead of choosing a convenient record.
- 01:57 — **12 · Simultaneous findings**: Fixture 200901 preserves late settlement, a 41-cent fee difference and a 127-cent amount difference; escalation is required.
- 02:08 — **13 · Scope of the result**: Both required abstentions and all four required escalations were correct. Six injected-note cases passed; broad prompt-injection safety is unmeasured.
- 02:18 — **14 · Historical benchmark preserved**: Raw-v1 remains 18/48 (37.5%). It tests diagnosis from raw evidence; v2 is rule-guided compliance, so the scores are not directly comparable.
- 02:29 — **15 · Independent human review**: Maker-checker remains enforced by the server. This read-only recording submits no recommendation, approval or financial change.
- 02:38 — **16 · Durable audit evidence**: Evaluation start/completion events are persisted. The original workflow video separately records analyst and supervisor escalation.
- 02:48 — **17 · Administration stays separate**: Worker visibility and controls live outside banking tasks. No service control is changed for this recording.
- 02:57 — **18 · Reviewer handoff**: The earlier workflow video is retained. This results walkthrough, complete pilot JSON and measured report will be added alongside it.

### Reproduce a read-only capture

`scripts/record-evaluation-demo.mjs` with `RECORD_EVAL_DEMO=1` records a chosen completed production
evaluation (`DEMO_EVALUATION_ID=4`) using privately supplied analyst credentials. It permits only
GET/HEAD browser requests; the login API is outside the recorded DOM. It never calls the evaluation
CLI or an investigation action. Replaying the recording script incurs no model cost. The older
`scripts/record-demo.mjs` remains an explicitly paid, state-changing workflow script; do not run it
without separate authorization.
