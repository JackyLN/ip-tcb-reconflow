# Adoption and reusable configuration

IMPLEMENTED: versioned provider profile creation by admin, exact CSV template download,
three replayable scenarios at 100/1,000/10,000 payments, source export, evidence drilldown,
human review and in-app worker alerts. Demo sources use SyntheticPay (200 fee basis points).

To add a provider: admin creates a distinct profile name, sets fee basis points and fee tolerance
in minor units, downloads template, replaces provider and external IDs, computes payout fees
using half-up rounding per payout, imports the synthetic CSV as analyst. Existing profile history
is immutable through the UI. CSV schema lists payout/payment/credit kind, IDs, provider, currency,
account, amount/refund/fee/adjustment/net integers, and UTC offset-free ISO timestamp.

PROPOSED training: 30-minute analyst evidence exercise, supervisor independent-decision exercise,
admin outage/kill-switch drill. Identify operations champions and weekly quality review owners.
NOT IMPLEMENTED: external notifications, bank connectors, bulk review, MFA/SSO, multi-tenant scope,
monthly provider fee changes on existing profiles or partial settlement support.
