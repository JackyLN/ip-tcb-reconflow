#!/usr/bin/env bash
# Run from /opt/reconflow after source synchronization. No shared-proxy or other-app mutation.
set -euo pipefail
umask 077
revision=${1:?pass the full source commit SHA}
if [[ ! $revision =~ ^[0-9a-f]{40}$ ]]; then
  echo 'Deployment requires an exact 40-character commit SHA.' >&2
  exit 2
fi
if [[ $(pwd -P) != /opt/reconflow ]]; then
  echo 'Run this script from /opt/reconflow.' >&2
  exit 2
fi
exec 9>/var/lock/reconflow-deploy.lock
flock -n 9 || { echo 'Another ReconFlow deployment is running.' >&2; exit 1; }
test -s .env.production
docker network inspect stayflow_backend >/dev/null
export RECONFLOW_IMAGE_TAG=$revision
compose=(docker compose --env-file .env.production -f compose.production.yaml)
"${compose[@]}" config --quiet
# Fail before restarting anything if public-demo settings are unsuitable.
python3 - <<'PY'
from pathlib import Path
values = dict(line.split('=', 1) for line in Path('.env.production').read_text().splitlines()
              if line and not line.startswith('#'))
assert values.get('COOKIE_SECURE', '').lower() == 'true', 'Secure cookies must be enabled'
assert values.get('DEMO_MODE', '').lower() == 'true', 'This VPS hosts only a synthetic demo'
assert len(values.get('SESSION_SECRET', '')) >= 32, 'A strong session secret is required'
PY
install -d -m 700 backups .secrets
previous=$(cat .deployed-sha 2>/dev/null || true)
restarted=0
completed=0
rollback() {
  status=${1:-$?}
  if [[ $status != 0 && $restarted == 1 && $completed == 0 ]]; then
    echo 'Deployment failed; retaining backup and attempting previous application image.' >&2
    if [[ $previous =~ ^[0-9a-f]{40}$ ]] && docker image inspect "reconflow-app:$previous" >/dev/null 2>&1; then
      RECONFLOW_IMAGE_TAG=$previous "${compose[@]}" up -d --no-build db app worker || true
    fi
    echo 'Database is never automatically restored. Diagnose migration compatibility before retry.' >&2
  fi
}
trap rollback EXIT
# Build while the old application can still serve traffic.
"${compose[@]}" build --pull app
"${compose[@]}" up -d --wait db
# Stop only this application's processes for a consistent backup/migration checkpoint.
"${compose[@]}" stop app worker
restarted=1
stamp=$(date -u +%Y%m%dT%H%M%SZ)
"${compose[@]}" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  > "backups/pre-deploy-$stamp-$revision.sql"
"${compose[@]}" run --rm --no-deps app alembic upgrade head
seed_output=$(mktemp .secrets/seed.XXXXXX)
trap 'status=$?; rm -f "$seed_output"; rollback "$status"' EXIT
"${compose[@]}" run --rm --no-deps app python -m reconflow.cli seed > "$seed_output"
# New accounts only; never print generated passwords into Actions logs.
if grep -q '@reconflow.demo' "$seed_output"; then
  grep '@reconflow.demo' "$seed_output" >> .secrets/demo-credentials.txt
  chmod 600 .secrets/demo-credentials.txt
fi
rm -f "$seed_output"
"${compose[@]}" up -d --no-build --wait --wait-timeout 180 db app worker
curl --fail --silent --show-error --retry 8 --retry-delay 3 --retry-all-errors \
  --max-time 15 https://tcb.jackylenghia.com/readyz >/dev/null
printf '%s\n' "$revision" > .deployed-sha
completed=1
printf 'Deployed ReconFlow %s to https://tcb.jackylenghia.com\n' "$revision"
