# Interview walkthrough

1. Explain synthetic boundary, workflow hypothesis, build/buy/do-nothing alternatives and no interviews.
2. Sign in as analyst using private generated credentials. Sources & imports -> mismatch -> 1,000.
3. Refresh run after worker completes. Show 20 payment lines/payout, refunds, net math and bank credit.
4. Open an exception, queue investigation, refresh. In no-key mode call it SIMULATED, not live AI.
   Open evidence anchors, four-tool trace, low confidence and missing independent confirmation.
5. Submit a human recommendation. Sign out, sign in as supervisor; approve/reject, inspect audit.
   Maker cannot decide their own proposal; auditors cannot mutate domain state.
6. Replay the same import. Counts/runs/cases remain unchanged. Launch 100-payment failure scenario;
   inspect RETRY_WAIT/attempts and job.failed audit followed by completion.
7. Sign in as admin, disable AI. New/queued investigations stop; deterministic runs continue.
8. Open measured operations, labeled offline evaluation and assumed business sensitivity. Explain gaps.
9. Open architecture/90-day rollout, pilot success/stop conditions and production security work.

Recommended live change: add SecondPay-v1 with a different fee policy using admin controls; import
new synthetic IDs with fee math updated. For a code demonstration, change a fee unit-test example,
run `uv run pytest tests/test_domain.py -k fee -q`, then explain half-up payout rounding.
Never secretly alter a matching tolerance or historical policy to make an exception disappear.

15-minute narrative: 3 minutes frame/alternatives, 8-minute app walkthrough, 2-minute architecture,
2-minute evaluation limitations and pilot plan. Live provider segment is optional and must be labeled.


## Observed recorded live run

An 87-second captioned actual browser recording is saved as ignored
`artifacts/live-demo/reconflow-live-demo.mp4` (H.264, no audio). Original WebM, screenshots,
chapters/result and usage JSON are alongside it. Password submission is outside the recorded DOM.

1. Analyst replays mismatch/1,000 -> import #1 -> run #1; existing data is reused.
2. Inspect payout #2 (USD): fee 18,899 minor units vs policy 18,799, difference USD 1.
3. Open [case #1](https://tcb.jackylenghia.com/exceptions/1); queue exactly one investigation.
4. Investigation #2 returns LIVE, with four scoped tools and observed evidence references.
5. Analyst proposes independent provider confirmation; distinct supervisor escalates proposal #2.
6. Case ends ESCALATED; audit records the different actor IDs. No money/finance adjustment.

Observed usage: two provider requests, 1,779 input/458 output tokens, summed request latency
7,608 ms; configured-price estimate USD 0.00339525. Model: gpt-5.4-mini-2026-03-17.
This is one successful workflow observation, not a graded holdout/model-accuracy result.

To record another authorized flow, use the explicit-opt-in README command. The recorder selects
an OPEN, uninvestigated fee case from that run; rerunning intentionally queues another live job.
Do not use it as a baseline test or rerun just to recreate this video.

Published recording and README: https://tcb.jackylenghia.com/docs/product/recorded-demo/ .
The same reviewed MP4 is versioned in public-docs/assets/demo for reproducible deployments.

## Controlled-v2 pilot results companion

The new [recording README](../public-docs/product/recorded-demo.md#controlled-v2-results-walkthrough)
contains an actual 188-second read-only production walkthrough with 18 captioned chapters.
The paid development pilot completed before filming: production #4, local snapshot #5,
12/12 accepted, 72/72 supported typed claims, 2/2 abstentions and 4/4 escalations. See the
[measured report and every inspected scenario](../public-docs/ai/controlled-v2-pilot-2026-11-08.md).

`RECORD_EVAL_DEMO=1 npm run demo:record-results` uses the existing private analyst credential
file and defaults to completed Evaluation #4. It performs no imports, investigation jobs or
review decisions; authentication is submitted outside the recorded DOM. Set DEMO_OUTPUT,
DEMO_BASE_URL, DEMO_EVALUATION_ID and DEMO_CREDENTIALS explicitly when reproducing another
approved/read-only recording. The original state-changing workflow recorder/video is preserved.
The 72-case live holdout requires separate approval; this recording does not authorize it.
