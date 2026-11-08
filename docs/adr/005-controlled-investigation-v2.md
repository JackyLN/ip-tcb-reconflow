# ADR 005: Controlled findings and a separate investigation contract

Status: IMPLEMENTED; offline verified; live development pilot measured; v2 live holdout NOT RUN.

Keep the modular monolith, database worker, four read-only tools and integer-money engine.
Preserve the raw-v1 benchmark and its 37.5% result as historical evidence. New jobs
explicitly use controlled-investigator-v2; legacy jobs/reports remain interpretable.

Supply a read-only deterministic assessment before inference: fee/net arithmetic, currency,
policy-window, candidate ambiguity and missing/conflicting evidence. Do not rewrite stored matches.
Use a closed material-claim contract with typed values and source relationships, canonical financial
summary and cataloged tentative hypotheses. This limits prose flexibility in return for testable
consistency. A citation ID alone is insufficient; authenticity and broader semantics remain outside
this validator's guarantee. Retain the existing JSON mode with server validation; do not claim a
provider's schema adherence would establish financial truth.

Keep original failed output and flags. New inconsistent reports are LIVE_REVIEW_REQUIRED rather
than repaired successful results. Block approval of pending/unsupported/mandatory-escalation
findings. Lock Control before Case/Proposal, refreshing current state, matching worker/audit order;
this serializes review with an in-flight bounded model call. The existing one-worker design and
external-call crash/retry limitations remain; no new distributed infrastructure or schema is needed.

Create a separate versioned synthetic benchmark with external expected rubrics. Classification in
track B tests agreement with supplied rules, not raw diagnosis. Offline scripted checks cannot
produce model scores. Live metrics and unsupported-claim scores are explicitly scoped to the
closed contract; expert semantic review and real-world source verification remain outstanding.

Tradeoffs: bounded catalog output is less expressive; canonical-summary deviations are conservatively
flagged; reviewed evidence fulfillment/override is not implemented, so unsupported cases must remain
escalated or rejected. No model can approve or mutate finance records. No human-productivity benefit
is claimed without a controlled study. See the public controlled-v2 method/status page.

Reference: https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=chat .

Pilot observation: the authorized development pilot accepted 12/12 reports,
72/72 typed claims, estimated USD 0.05484750. This supports demo compatibility with the existing
contract; it does not establish real-bank safety or alter the decision to require human review.
