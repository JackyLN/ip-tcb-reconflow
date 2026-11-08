.PHONY: configure up down migrate seed test lint eval eval-v2 smoke assets docs-check
configure:
	python3 scripts/configure.py
up:
	docker compose up --build -d
# Keeps persistent volumes. Reset is an explicit, separate CLI command.
down:
	docker compose down
migrate:
	docker compose run --rm app alembic upgrade head
seed:
	docker compose run --rm app python -m reconflow.cli seed
test:
	uv run pytest -q
lint:
	uv run ruff check .
	uv run ruff format --check .
eval:
	docker compose run --rm app python -m reconflow.cli eval
smoke:
	uv run python scripts/smoke.py
assets:
	npm ci --ignore-scripts
	npm run build

docs-check:
	uv run python -m scripts.check_public_docs

# Scripted controlled track; never calls a provider without explicit --live.
eval-v2:
	mkdir -p artifacts
	(umask 077; docker compose run --rm app python -m reconflow.cli eval --track controlled-v2 > artifacts/controlled-v2-offline.json)
	python3 -c 'import json; r=json.load(open("artifacts/controlled-v2-offline.json")); assert r["offline_contract_valid"] == r["cases_run"] == 72 and r["usage"]["requests"] == 0 and r["model_accuracy"] is None; print("PASS: 72 scripted v2 contracts, zero provider requests; not model accuracy")'
