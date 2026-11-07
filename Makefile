.PHONY: configure up down migrate seed test lint eval smoke assets
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
