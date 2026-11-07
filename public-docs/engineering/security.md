# Security and governance boundary

ReconFlow is a public **synthetic-only demonstration**, not production-certified banking software.
The public handbook is readable without an account. The operations console requires authentication.

## Implemented controls

- Generated private demo credentials, Argon2 password hashes and expiring server-side sessions.
- Secure cookies on the HTTPS deployment, CSRF protection and server-side role checks.
- Maker-checker enforcement: proposer and decision maker must differ; auditors cannot mutate cases.
- Integer money, validated imports, unique source identities, replay-safe DB effects and safe CSV exports.
- Bounded read-only model tools, schema checks, citation membership checks, quotas and an AI kill switch.
- Application append-only audit events, a serialized hash chain and a PostgreSQL update/delete guard.

## Model and evidence risk

Tool output and imported strings are untrusted data. The model cannot choose arbitrary SQL/HTTP
requests, write financial records, approve a proposal or execute a payment. Human review is required.
A valid citation ID proves the evidence was available; it does **not** prove a statement is true.
Semantic claim support and calibrated confidence remain unmeasured without independent grading.

## Explicit limitations

The workspace is single-merchant and synthetic, with no bank SSO/MFA, production tenant isolation,
separate least-privilege DB roles or externally anchored immutable audit storage. A database owner
can disable database guards or rewrite history. Backup restore drills, independent penetration
assessment and real-bank data governance are not completed.

Public docs render repository-reviewed Markdown with raw HTML disabled. Only files in the dedicated
`public-docs/` tree are published; internal operational runbooks, environment files and generated
credentials are not part of this documentation catalog. Mermaid uses strict mode and local assets.

## Proposed production work

Bank identity integration, scoped integrations, retention approvals, managed secrets, independent
security review, incident/restore drills and a supervised risk-approved pilot are target-state work.
Read the [pilot rollout](../rollout/plan.md) for proposed gates and stop conditions.
