# Decision memo: supervised settlement investigation

PROPOSED decision: pilot a Python modular monolith that deterministically reconciles provider
payouts to bank credits, with bounded advisory AI for exceptions and independent human closure.
The user is a settlement analyst; the reviewer is an operations supervisor. Workflow ownership
and present pain are hypotheses pending stakeholder interviews.

Three directions: do nothing retains manual spreadsheets and avoids integration cost but leaves
repeatability and ownership uncertain; buy an established reconciliation product reduces custom
maintenance but needs vendor, integration, privacy and control evaluation; build a narrow supervised
workflow allows explicit evidence and safety rules but creates engineering and governance burden.
No vendor prices or bank savings were researched or asserted. Build is the interview prototype
choice; a production buy/build decision needs real requirements and commercial proposals.

The product groups payments into payouts before matching credits, preserves imported provenance,
flags ambiguities, and records a human review chain. AI cannot approve or mutate finance data.
Business value is projected capacity, not cash savings: see the editable USD assumptions at
/reports/impact. No measured human baseline or realized ROI exists.

PROPOSED 90-day gates: >=95% eligible payout batches matched or assigned within 24h,
>=20% shorter investigation turnaround against a measured control, >=99% citation validity,
zero unauthorized actions, positive risk-adjusted capacity value. Stop for a material arithmetic
error, unauthorized action, material unsupported AI claim or negative value. Disable AI, retain
human workflow and diagnose before restart. Pilot gates are not prototype achievements.
