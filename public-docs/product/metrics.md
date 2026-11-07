# Measurement contract

North star (PROPOSED): eligible batches matched or assigned to a documented owner within SLA /
all eligible batches, in a named period, with zero unauthorized financial changes.

IMPLEMENTED proxy: current database snapshot across all imports; numerator is matched payouts
plus cases with a human proposal, escalation or approved resolution. Denominator is processed
payouts. OPEN/INVESTIGATING unassigned cases do not count as owned. No SLA achievement claim.

MEASURED: persistent payment/payout/match counts, unresolved cases, pending proposals, distribution,
oldest unresolved age, median completed-run worker time in ms (queue/import time excluded).
Source: SQLAlchemy database queries, not chart fixtures. VND/USD amounts are never combined.

PROPOSED supporting metrics: investigation turnaround, audit-complete resolution rate, semantic
AI evidence validity. NOT IMPLEMENTED: period filters, SLA compliance, percentiles for review
turnaround, human labor baseline and A/B assignment. Pilot plan: shadow baseline then staged
teams/control; compare case severity and provider mix, pre-register stop criteria, grade independently.
