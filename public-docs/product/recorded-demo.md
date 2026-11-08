# Recorded live demo

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
