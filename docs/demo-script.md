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
