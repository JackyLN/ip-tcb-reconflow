# ReconFlow

Accountable merchant settlement operations: turn payment evidence into reconciled payouts,
explained exceptions and independently reviewed outcomes.

Built for the **Techcombank AI Transformation Division Expert Challenge**: frame a banking
problem, build a working product and automate safely.

> **SYNTHETIC DEMONSTRATION.** This prototype uses synthetic records only. It does not execute
> payments, integrate with a real bank or establish facts about Techcombank's internal operations.
> Documentation and videos are public; the operations console requires separate sign-in.

## Reviewer journey

1. [Understand the problem — hypothesis and selection](framing/index.md)
2. [Watch the latest demo — 3:08 results walkthrough](product/recorded-demo.md#controlled-v2-results-walkthrough)
3. [Explore the console — authenticated synthetic workspace](/)
4. [Inspect the evidence — original results and limitations](ai/evaluation.md)
5. [Understand the architecture — controls and trade-offs](engineering/index.md)
6. [Review the roadmap — proposed bank rollout](rollout/plan.md)

## Why this banking problem

**ASSUMED problem hypothesis:** settlement analysts need to explain differences between provider
payouts and bank credits. Fees, refunds, timing, missing records and ambiguous references can
make the evidence difficult to reconcile and leave exception ownership unclear.

We selected it for inspectable financial arithmetic, a repeatable workflow and a bounded AI role.
Many payments aggregate into payouts, so individual payment matching misses the core problem.
The [decision memo](framing/decision-memo.md) keeps buy/build/do-nothing trade-offs visible.

The vision is an evidence-led workbench where every discrepancy has an explanation, an owner
and an accountable review path. **NOT VALIDATED:** no Techcombank stakeholder interviews or
real-bank productivity baseline have been collected. See the [discovery gaps](framing/discovery.md).

## From evidence to accountable review

1. **Payment evidence**
   Import payments, refunds, provider payouts and bank credits.
2. **Reconciliation**
   Check payout totals, fees, currency, timing and candidate matches.
3. **AI investigation**
   Use read-only evidence; distinguish facts, hypotheses and gaps.
4. **Human review**
   An analyst recommends; a different supervisor decides.
5. **Audit & measurement**
   Retain provenance, decisions, model outputs and measured results.

[Follow the complete workflow](product/workflow.md).

## What is implemented

**IMPLEMENTED:** synthetic CSV intake and replay-safe reconciliation; integer VND/USD arithmetic;
exception investigation; independent maker-checker review; server-side permissions; audit history;
durable jobs with retry/recovery; an AI kill switch; operational reports and an evaluation dashboard.
[Explore the working capabilities](product/index.md).

**Solution boundary:** deterministic rules establish financial findings. AI proposes evidence-linked
explanations and safe follow-up; inconsistent findings are retained and escalated. AI cannot approve
financial decisions, move money, change balances or execute arbitrary SQL/HTTP. **SIMULATED**
no-key responses are explicitly scripted. [Read the security and human-review boundaries](engineering/security.md).

## Measured AI evidence

These benchmarks answer **different questions**. Their scores are not equivalent measures of
accuracy and should not be presented as a before/after improvement.

| Track | Actual result | What the result means |
| --- | --- | --- |
| [Raw-v1 holdout](ai/holdout-2026-11-08.md) | **MEASURED: 18/48 correct (37.5%)** | Classification from raw synthetic evidence. All 30 failures remain available; unsuitable as an authoritative classifier. |
| [Controlled-v2 development pilot](ai/controlled-v2-pilot-2026-11-08.md) | **MEASURED: 12/12 accepted; 72/72 typed claims supported** | Agreement with supplied deterministic findings and a closed claim contract. Required abstentions 2/2; escalations 4/4. Small development sample, not a holdout result. |

The pilot used 24 provider requests; p50/p95 latency **2,869/6,299 ms** and **ESTIMATED** cost
**USD 0.05484750**. Original outputs, traces and usage are linked in the reports.
**NOT MEASURED:** controlled-v2 live holdout, unrestricted semantic factuality, source authenticity
or human productivity gains. The 72-case live holdout is **NOT RUN**, pending separate authorization.

## Product ownership approach

Validate the problem with operations, risk and IT; agree exception ownership and closure evidence;
prioritize safe, complete workflows; measure turnaround and quality against an observed control.

**PROPOSED bank ownership:** Product/BA prioritizes the backlog and acceptance gates; operations
owns labels and case outcomes; risk approves boundaries; engineering owns reliability and controls.
These bank responsibilities are not yet assigned or validated.
See the [measurement contract](product/metrics.md) and [adoption approach](product/adoption.md).

## Prototype now, proposed bank rollout next

| Stage | Scope | Evidence needed to proceed |
| --- | --- | --- |
| **IMPLEMENTED — prototype now** | Synthetic end-to-end workflow, deployed console, recorded demos and scoped live AI measurements. | Existing source records, tests and measured reports are inspectable. This is not a bank deployment. |
| **PROPOSED — first 30 days** | Validate users, source quality, ownership, baseline and data access; prepare shadow connectors. | Trusted source totals, replay checks, privacy/retention decisions and risk acceptance. |
| **PROPOSED — days 31–60** | One-team supervised pilot with training and a staged/control comparison. | Independent quality grading, no unauthorized actions and measured benefit against the control. |
| **PROPOSED — days 61–90** | Expand one provider/team at a time, with named owners, runbooks and cost/quality monitoring. | Previously agreed gates continue to hold; stop or roll back when they fail. |

The [30/60/90-day plan](rollout/plan.md) defines gates and stop conditions. Bank connectors,
stakeholder validation, a real operations pilot and realized ROI remain **NOT IMPLEMENTED / NOT MEASURED**.
Business inputs are **ASSUMED**, not achieved savings.

## Read the evidence labels

| Label | Meaning |
| --- | --- |
| **IMPLEMENTED** | A real path exists in this prototype. |
| **MEASURED** | An observed result from an identified verification or evaluation run. |
| **SIMULATED** | Scripted offline behavior, not model inference. |
| **ASSUMED** | An illustrative input or hypothesis, not a bank-supplied fact. |
| **PROPOSED** | Future work or a target, not an achieved outcome. |
| **NOT IMPLEMENTED / NOT MEASURED** | An explicit gap or limit on what can be claimed. |

Use the title search, section navigation and full library below for a deeper review.
[Documentation authoring](authoring/index.md) explains Markdown, diagrams and source inspection.
