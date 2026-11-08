# Shared VPS deployment

Target: `https://tcb.jackylenghia.com` on `187.127.220.131`.
SSH operator alias: `ssh jackylenghia` (root). Application directory: `/opt/reconflow`.
LIVE and verified on the deployed source. This is a public **synthetic-only demo**, with secure session
cookies and no LLM key. Deployed source: `31018ede59dcfd00701eb21471f60ab546be5140`.
App/worker/DB and public login/readiness, synthetic end-to-end flow and browser checks passed.
GitHub CI succeeded: https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42415477106 .
Hosted CD subsequently succeeded after user-managed secret setup:
https://github.com/JackyLN/ip-tcb-reconflow/actions/runs/42421131938 .

## Topology and bootstrap

The existing `stayflow-caddy-1` owns public ports 80/443 and its persistent certificate storage.
`/opt/stayflow/deploy/Caddyfile` keeps the Stayflow and Lite Trading Bot sites and adds only
`deploy/Caddyfile.snippet` for this hostname. Do not start ReconFlow's standalone Caddy on this VPS.

`compose.production.yaml` creates isolated `reconflow` app/worker/PostgreSQL services and a
persistent `reconflow_db_data` volume. No ReconFlow container publishes a host port. Only the app
joins external `stayflow_backend`, using alias `reconflow-app`; DB/worker stay on the project's
separate backend network. The shared proxy sends this hostname to `reconflow-app:8000`.
Caddy manages trusted HTTPS certificates and HTTP-to-HTTPS redirects.

First setup (operator): synchronize source to `/opt/reconflow`, run
`python3 scripts/configure_production.py` there, validate/add the Caddy snippet, then run
`bash scripts/deploy.sh FULL_COMMIT_SHA`. The configure command creates a mode-600
`.env.production` with separate generated DB/session secrets, secure cookies and DEMO_MODE=true;
rerunning it preserves the existing file. Never copy the local development `.env` to this server.

Before modifying the shared Caddyfile, save a timestamped backup, validate a candidate in the
existing Caddy container, then update the bind-mounted file **in place** and reload Caddy.
An atomic rename can leave a file bind mount pointing at the old inode. Validate existing sites
after reload. Preserve this site block when redeploying/updating the shared Stayflow proxy.
The reusable site snippet is committed; the other app's configuration is not owned
or overwritten by ReconFlow CD. DNS for this hostname must resolve to this server.

## GitHub Actions setup (user-managed secrets)

Workflow: `.github/workflows/cd.yml`, named **CD**, manually triggered (`workflow_dispatch`).
It checks out main, runs lint/tests/JavaScript syntax validation, then deploys that exact verified
SHA. Runs are limited to actor `JackyLN`, use the `production` environment and serialize deployments.
It follows the SSH/rsync pattern in Lite Trading Bot's CD workflow.

Set these **repository secrets**, or the same names in the `production` environment:

| Secret | Value |
| --- | --- |
| `VPS_HOST` | `187.127.220.131` |
| `VPS_USER` | `root` |
| `VPS_SSH_PRIVATE_KEY` | Full multiline private key whose public key is authorized for root on this VPS |
| `VPS_KNOWN_HOSTS` | Pinned SSH host-key line(s) for `187.127.220.131` |

The operator alias `jackylenghia` is local SSH configuration and is not available on GitHub runners.
Use the actual IP and username above. The key filename on the runner does not require the key to
be Ed25519; SSH supports an RSA key stored in that file as well. A dedicated deployment key is
preferable to a personal key; key creation/installation and secret setup are explicitly user-owned.
This session does not upload or change deployment credentials. A copy of the server's public
Ed25519 host-key line is provided locally at `artifacts/vps-known-hosts` for the known-hosts secret;
it was obtained over the existing trusted SSH connection, not blindly trusted from a network scan.

After setting secrets, open Actions → CD → Run workflow → main. The first user-configured hosted CD run succeeded (42421131938); validate subsequent runs
against their own revision and public readiness result. The current GitHub CLI account has only repository READ
permission, so it cannot set secrets or dispatch CD; Git SSH is authenticated separately as JackyLN.

## Deployment behavior and operation

The script locks deployments, validates secure-demo settings, builds an immutable commit-tagged
image while the previous app can serve, starts/checks DB, then stops only ReconFlow app/worker.
It saves a consistent PostgreSQL dump under `backups/`, applies Alembic migrations and seeds only
missing demo accounts. It starts app/worker/DB and waits for readiness/heartbeat, then verifies
public HTTPS before recording `.deployed-sha`. Brief ReconFlow downtime is expected at migration.
Stayflow and Lite Trading Bot processes are never stopped by this script.

Generated account passwords are saved only to `/opt/reconflow/.secrets/demo-credentials.txt`
(mode 600), not Actions logs. Retrieve privately with:
`ssh jackylenghia 'cat /opt/reconflow/.secrets/demo-credentials.txt'`.
The deploy workflow never resets data or replaces `.env.production`, backups, `.secrets/` or
`.deployed-sha` during synchronization. No scheduled cleanup deletes backup/image history.

For manual create/run/up commands, export RECONFLOW_IMAGE_TAG from .deployed-sha so the
existing commit-tagged image is used. Use a command array or repeat this prefix on the VPS:
`docker compose --env-file .env.production -f compose.production.yaml`.

```sh
cd /opt/reconflow
export RECONFLOW_IMAGE_TAG=$(cat .deployed-sha)
docker compose --env-file .env.production -f compose.production.yaml ps
docker compose --env-file .env.production -f compose.production.yaml logs --tail 100 worker
curl --fail https://tcb.jackylenghia.com/readyz
```

On failure after restart begins, the script attempts to start the prior recorded image when one
exists. **It never automatically restores the database.** Migrations must remain compatible or
require an operator-reviewed recovery plan. Restore dumps into an isolated DB first; never issue
`down -v` or the demo reset command as part of routine deployment.

Live model credentials remain absent. Configure trusted provider settings manually in the server
`.env.production` only when deliberately enabling live inference. Root/Docker deployment access,
shared proxy networking, no bank SSO/MFA and no externally anchored audit remain prototype limits.

References consulted: Caddy automatic HTTPS https://caddyserver.com/docs/automatic-https and
GitHub Actions secrets https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets .
