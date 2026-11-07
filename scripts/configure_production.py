"""Generate isolated VPS secrets once; preserve existing deployment configuration."""

import os
import secrets
from pathlib import Path


def main() -> None:
    path = Path(".env.production")
    password = secrets.token_hex(24)
    content = f"""# Synthetic ReconFlow public demo; secrets stay on this server.
POSTGRES_DB=reconflow
POSTGRES_USER=reconflow
POSTGRES_PASSWORD={password}
DATABASE_URL=postgresql+psycopg://reconflow:{password}@db:5432/reconflow
SESSION_SECRET={secrets.token_hex(48)}
DEMO_MODE=true
COOKIE_SECURE=true
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=
LLM_API_KEY=
LLM_INPUT_USD_PER_MILLION=0
LLM_OUTPUT_USD_PER_MILLION=0
"""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("Existing .env.production preserved.")
        return
    with os.fdopen(fd, "w") as output:
        output.write(content)
    print("Created private .env.production for the synthetic HTTPS demo (no LLM key).")


if __name__ == "__main__":
    main()
