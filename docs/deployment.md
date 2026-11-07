# VPS deployment and operations

IMPLEMENTED Docker Compose target; tested locally on Docker Desktop. External VPS, DNS and public
TLS issuance are NOT VERIFIED. Baseline needs no LLM API key. Use only synthetic/public records.

On a clean machine with Docker Compose, Git and Python 3:

```sh
make configure
docker compose build
docker compose up -d db
make migrate
make seed
# Save generated role credentials privately; they are printed only for newly created users.
docker compose up -d --wait
```

Open http://localhost:8080 for local use. To test the exact HTTP workflow, preserve first-seed
stdout privately: `(umask 077; make seed > artifacts/demo-credentials.txt)` after creating artifacts.
Do this on the first seed only; later seed commands preserve users and do not print old passwords.
`make smoke` expects this ignored private file, or pass `--credentials` to scripts/smoke.py.
Do not publish artifacts/demo-credentials.txt or .env. Fresh installation creates persistent db_data,
caddy_data and caddy_config volumes. `make down` keeps them; no reset occurs on startup.

For public HTTPS: set DNS A/AAAA to the VPS, open 80/443, edit private .env:
SITE_ADDRESS=your-domain.example, HTTP_PORT=80, HTTPS_PORT=443, COOKIE_SECURE=true.
Keep a strong generated SESSION_SECRET and DB password; set DEMO_MODE=true only on the isolated
synthetic demo. Run `docker compose up --build -d --wait`. Caddy obtains TLS automatically.
Do not set COOKIE_SECURE=false on a public deployment. DB and app have no published ports.

Commands:
- `make up/down/migrate/seed/test/lint/eval/smoke/assets`.
- `docker compose exec -T app python -m scripts.postgres_checks` uses a temporary schema and
  verifies competing job claims, hash chaining and the deployed append-only UPDATE guard.
- `docker compose run --rm app python -m scripts.benchmark` uses a temporary schema and measures
  100/1,000/10,000 synthetic payment processing without changing demo records.
- `docker compose logs --tail 100 worker` and /operations/health show failures/heartbeat.
- A killed worker can be restarted with `docker compose restart worker`; an expired lease recovers
  after 180 seconds. Injected failures retry after 2/4 seconds, dead-letter on third failure.

Backup: `docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql`.
Protect/encrypt backup.sql outside VCS. Stop app/worker before a restore to a separate validated
instance; restore/retention automation and a real restore drill are NOT IMPLEMENTED.

Dangerous optional demo reset (stop app/worker first, destroy only synthetic data):
`docker compose run --rm app python -m reconflow.cli reset --confirm-synthetic-reset --confirm-destroy-all-demo-data`.
Requires DEMO_MODE=true and both confirmations. Accounts/passwords are regenerated; save privately.
No production mutation or reset occurs by default. The CLI is operator-only, never a web/AI action.

Production security work remains: SSO/MFA, tenant isolation, least-privilege DB roles, external
immutable audit storage, provider egress controls, dependency review, operator alert delivery,
recovery drills and independent assessment. No banking production assurance is claimed.
