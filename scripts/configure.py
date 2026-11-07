"""Create local secrets without overwriting an existing .env."""

import secrets
from pathlib import Path

path = Path(".env")
password = secrets.token_hex(24)
content = (
    Path(".env.example")
    .read_text()
    .replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={password}\n")
    .replace("CHANGE_ME", password)
    .replace("SESSION_SECRET=\n", f"SESSION_SECRET={secrets.token_hex(48)}\n")
)
try:
    with path.open("x") as output:
        output.write(content)
    path.chmod(0o600)
    print("Created private .env for local synthetic demo (HTTP port 8080).")
except FileExistsError:
    print("Existing .env preserved; review required configuration manually.")
