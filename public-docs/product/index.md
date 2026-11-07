# Product guide

ReconFlow supports a bank-side merchant settlement **product hypothesis**: operations analysts
need to explain differences between provider payouts and bank credits, with an accountable review path.

## Working prototype

1. Import synthetic payment, payout and bank-credit evidence.
2. Aggregate many payments into each payout and calculate its expected net using integer money.
3. Match only a single eligible bank credit; record an exception when the evidence disagrees.
4. Read the evidence and optionally request a bounded advisory AI investigation.
5. Submit a human recommendation and have a different supervisor decide it.
6. Inspect the audit, replay the same source safely and examine worker retry history.

The [measurement contract](metrics.md) distinguishes stored prototype metrics from proposed pilot outcomes.

The [workflow walkthrough](workflow.md) explains each step. The [adoption guide](adoption.md)
shows reusable provider policies, source templates and training assumptions.

## Roles

| Role | Responsibility |
| --- | --- |
| Analyst | Import, investigate and propose a resolution. |
| Supervisor | Investigate and decide another person's proposal. |
| Manager | Read operational and business reports. |
| Auditor | Read evidence and audit history. |
| Administrator | Manage provider profiles and automation controls. |

Access to the console requires privately supplied demo credentials. This public handbook grants
no access to uploaded data, role changes, live model calls or mutation endpoints.

## Supported scenarios

- **Clean:** coherent payment-to-payout-to-credit evidence.
- **Mismatch:** fees, refunds, missing/late/wrong-currency credits and duplicate candidates.
- **Failure:** an injected first-attempt worker error, retry and replay behavior.

Each generator supports 100, 1,000 and 10,000 synthetic payments, with 20 payments per payout.
The scenarios are reproducible, not historical bank datasets.
