IMPLEMENTED: FastAPI/Jinja2 modular monolith, PostgreSQL 16, SQLAlchemy/Alembic,
one Python worker, DB queue, Caddy; local Tailwind, HTMX and Chart.js assets.
Browser -> Caddy -> app -> PostgreSQL <- worker -> optional configured LLM HTTPS.
Payment lines (including cumulative refunds) -> payout -> one bank credit.
Partial/many-to-many/cross-currency settlement is unsupported and not forced matched.

App: server-side opaque sessions, Argon2, CSRF, server role checks, no role headers.
Worker: leased jobs, SKIP LOCKED, row-lock fencing, atomic handler/completion commit,
exponential retry, three-attempt dead letter, heartbeat. One worker is the supported target.
Reconciliation is integer-only. AI reads four bounded evidence tools; schema/citation
membership gates cannot prove semantic truth. AI never creates proposals or finance writes.

Public synthetic demo data only. Finance data in a bank deployment would be confidential.
Raw imports are retained for provenance. Proposed demo retention: reset between demos,
operator-encrypted daily backups retained 7 days. Automated retention is NOT IMPLEMENTED.
Audit is application append-only, hash-chained and serialized. Database owner can rewrite
history: this is not a WORM ledger or production banking certification.

PROPOSED production: bank SSO/MFA, tenant scoping, managed secrets and rotation, separate
least-privilege DB roles, external audit anchoring, security review, alert delivery, backup
restore drills, production incident/retention governance, supervised integration connectors.
MVP is a single synthetic merchant workspace, not a multi-tenant banking platform.

Implementation references: PostgreSQL SELECT/locking semantics:
https://www.postgresql.org/docs/16/sql-select.html
FastAPI templates/static-files integration:
https://fastapi.tiangolo.com/advanced/templates/
