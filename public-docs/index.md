# ReconFlow handbook

An evidence-led view of merchant settlement operations: the product hypothesis, the working
prototype, its engineering decisions and a proposed path to a supervised pilot.

**This is a synthetic interview demonstration.** It does not execute payments, integrate with a
real bank or establish facts about Techcombank's internal operations. You can read this handbook
without an account; the operations console uses separate authenticated access.

![A reading path from the brief through the prototype to its evidence](assets/reading-flow.svg)

## Start with the question you need to answer

- **What is built?** Read the [product guide](product/index.md) and [end-to-end workflow](product/workflow.md).
- **Why this problem and direction?** See the [framing](framing/index.md), [decision memo](framing/decision-memo.md) and [business assumptions](framing/business-case.md).
- **How does it work safely?** Explore the [architecture](engineering/index.md), [security boundaries](engineering/security.md) and [decision records](engineering/decisions/index.md).
- **What can the AI actually do?** Read the [AI design](ai/index.md) and [evaluation limits](ai/evaluation.md).
- **How would a team adopt it?** See the [rollout proposal](rollout/plan.md).

## How to read the evidence labels

| Label | Meaning |
| --- | --- |
| **IMPLEMENTED** | A real path exists in this prototype. |
| **MEASURED** | A result observed from the prototype or an identified verification run. |
| **ASSUMED** | An input chosen for illustration, not a bank-supplied fact. |
| **SIMULATED** | Scripted offline behavior, not model inference. |
| **PROPOSED** | A pilot target or future design, not an achieved outcome. |
| **NOT IMPLEMENTED / NOT MEASURED** | An explicit limit on what can be claimed. |

## Explore the handbook

The library below lists every published Markdown page, including nested decision records.
Use the sidebar to browse sections, the right-hand outline on desktop to jump within a page,
and the previous/next links to follow the reading order. The search field matches document titles.

Authors can add another `.md` file under `public-docs/` and it will appear automatically.
See [writing documentation](authoring/index.md) for tables, code, footnotes and Mermaid diagrams.

Watch the [recorded live demo](product/recorded-demo.md) with its chapters and measured results.

Read the [48-case live evaluation and all failures](ai/holdout-2026-11-08.md):
18/48 correct (37.5%), with synthetic evidence and measured usage available for review.
