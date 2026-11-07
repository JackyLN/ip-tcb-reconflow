# Security boundary and limitations

IMPLEMENTED: Argon2 passwords, generated independent role credentials, opaque server-side sessions
(8 hours), signed HttpOnly SameSite=Lax cookies, CSRF on every mutating web form, server role checks,
maker != checker, admin-only controls, DB-unique source identities, atomic/replay-safe imports/jobs,
integer money, file size/row caps, formula-safe CSV exports, local assets, CSP, no exposed DB port,
nonroot/read-only app and worker containers, secrets excluded from VCS/build, login rate limit,
AI daily quotas and bounded read-only tools, PostgreSQL audit UPDATE/DELETE guard and hash chain.

Threats: source notes can try prompt injection; tools treat them as data, schemas/evidence allowlists
reject invented references, human review remains mandatory. A cited statement may still be false:
semantic support is not guaranteed. User-supplied identifiers can reach HTML but Jinja autoescapes.
Exports prefix formula-leading cells, so unsafe identifiers may change on export; preserve original
raw CSV only within the database for provenance. No SQL/HTTP tool is available to AI.

Roles: analyst imports/investigates/proposes; supervisor investigates/proposes/decides others' proposals;
manager reads reports; auditor reads; admin launches synthetic/import data, manages profiles/AI.
All can read this single synthetic workspace, sign in/out; there is no per-merchant tenant isolation.

NOT IMPLEMENTED/VERIFIED: bank SSO/MFA, password rotation/recovery UI, per-IP distributed throttling,
separate DB application/migration roles, external WORM audit anchor, bank data retention/consent,
independent penetration test or public deployment. Login buckets grow without scheduled cleanup;
behind Caddy, app sees a proxy address, so throttling is shared and can cause availability limits.
PostgreSQL owner can disable the audit trigger or truncate history; no tamper-proof claim.
Infrastructure logs can contain network metadata; no request payload/password/model key is logged.
CLI seed intentionally prints generated credentials once to operator stdout; protect that output.
Provider URL is operator configuration, not a model input; configure trusted HTTPS egress only.

Local demo uses HTTP and COOKIE_SECURE=false. HTTPS and secure cookies are mandatory instructions
for public deployment. Data must remain synthetic/public even after deploying this prototype.
