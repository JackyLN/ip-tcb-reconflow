# ADR 004: GPT-5.4 mini for demo investigations

Date: 2026-11-08
Status: **Accepted model choice; adapter integration and live evaluation pending.**

## Decision and rationale

Use **GPT-5.4 mini**, pinned to `gpt-5.4-mini-2026-03-17`, as the target OpenAI model
for ReconFlow's advisory exception investigations. The dated snapshot makes the selected version
explicit for repeatable interview demonstrations. The choice balances small-model cost with the
tool-calling and structured-output capabilities needed for evidence-based explanations.

Financial reconciliation and policy decisions remain deterministic Python. The model reads scoped
evidence, proposes explanations/next steps and always requires human review. Selecting this model
does not grant it approval rights or financial-write capabilities.

This is a design judgment informed by documented capabilities, **not a measured claim** that the
model meets ReconFlow's accuracy or latency requirements. A larger flagship is not justified before
this candidate is evaluated; a smaller/cheaper model remains an alternative if it passes the same
holdout and safety checks. Provider/model configuration stays replaceable.

## Target configuration and cost assumptions

Set these values in the privately managed server environment only when ready to enable
live inference, alongside the separately managed `LLM_API_KEY`:

```dotenv
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-5.4-mini-2026-03-17
LLM_INPUT_USD_PER_MILLION=0.75
LLM_OUTPUT_USD_PER_MILLION=4.50
```

Published standard text rates checked on 2026-11-08: **USD 0.75 per million uncached input tokens**
and **USD 4.50 per million output tokens**. These are provider rate assumptions for the application's
cost estimates, not observed spend. Recheck rates before live evaluation; cached-input discounts,
regional processing, future pricing changes and provider billing may differ from the simple estimator.

## Integration work still required

- [ ] Update the request adapter to use `max_completion_tokens` instead of deprecated `max_tokens`.
- [ ] Explicitly set request parameter `reasoning_effort` to `none` initially, as the starting
  configuration for the demo's bounded output/time budget. This is not a latency measurement.
- [ ] Test the updated request contract with mocked HTTP responses, retaining all tool/evidence,
  quota, kill-switch and human-review gates.
- [ ] Verify model availability and real request compatibility with the configured API project.
- [ ] Run a small explicitly authorized live holdout evaluation, inspect failures/tool traces and
  record actual usage, estimated cost and latency before relying on it during an interview.

`reasoning_effort` is a planned request parameter, **not an existing environment setting**.
The model choice alone does not implement these changes. No source code, runtime configuration,
server secrets or deployment is changed by recording this decision. No paid API calls were made
for this documentation update. Existing no-key SIMULATED behavior remains available.

## Sources and follow-up

- [Official OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini):
  model snapshot, reasoning options, function calling, structured outputs and published rates.
- [Official Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create):
  `max_completion_tokens` and deprecation of `max_tokens`.
- [Evaluation contract](../../ai/evaluation.md): synthetic holdout, explicit live command, reporting limits.
- [ADR 002](002-deterministic-financial-truth.md): deterministic finance and advisory-only AI boundary.
