"""Explicit operational commands; no destructive default and no implicit paid inference."""

import argparse
import json
import secrets

from sqlalchemy import select

from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.models import Control, Provider, User
from reconflow.security import hasher
from reconflow.services.audit import append


def seed() -> None:
    """Add demo accounts once; print independent generated passwords once to operator stdout."""
    if not settings().demo_mode:
        raise ValueError("Seed requires DEMO_MODE=true")
    credentials = []
    with SessionLocal.begin() as db:
        if not db.get(Control, 1):
            db.add(Control(id=1))
        if not db.scalar(select(Provider).where(Provider.name == "SyntheticPay")):
            db.add(Provider(name="SyntheticPay", fee_bps=200, tolerance=0))
        db.flush()
        for role in ("analyst", "supervisor", "manager", "auditor", "admin"):
            email = f"{role}@reconflow.demo"
            if db.scalar(select(User).where(User.email == email)):
                continue
            password = secrets.token_urlsafe(18)
            db.add(User(email=email, role=role, password_hash=hasher.hash(password)))
            credentials.append((email, password))
        append(db, "cli", "demo.seeded", "workspace", new_accounts=len(credentials))
    for email, password in credentials:
        print(f"{email}  {password}")
    print("Save new credentials privately. Existing users and passwords were preserved.")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed")
    generator = sub.add_parser("dataset")
    generator.add_argument("--count", type=int, default=1000, choices=[100, 1000, 10000])
    generator.add_argument(
        "--scenario", default="mismatch", choices=["clean", "mismatch", "failure"]
    )
    generator.add_argument("--labels", action="store_true")
    evaluation = sub.add_parser("eval")
    evaluation.add_argument(
        "--live", action="store_true", help="Explicitly authorize paid provider calls"
    )
    evaluation.add_argument("--limit", type=int, default=48)
    reset = sub.add_parser("reset")
    reset.add_argument("--confirm-synthetic-reset", action="store_true")
    reset.add_argument("--confirm-destroy-all-demo-data", action="store_true")
    args = parser.parse_args()
    if args.command == "dataset":
        from reconflow.services.ingestion import scenario_csv, scenario_labels

        print((scenario_labels if args.labels else scenario_csv)(args.count, args.scenario), end="")
    elif args.command == "seed":
        seed()
    elif args.command == "eval":
        from reconflow.evaluation import evaluate

        with SessionLocal() as db:
            print(json.dumps(evaluate(db, args.live, args.limit, checkpoint=True), indent=2))
    elif args.command == "reset":
        if not (
            settings().demo_mode
            and args.confirm_synthetic_reset
            and args.confirm_destroy_all_demo_data
        ):
            parser.error("Reset requires DEMO_MODE and both explicit confirmation flags")
        from sqlalchemy import text

        from reconflow.db import Base, engine

        # Local developer command only; cannot be invoked through web/AI.
        with engine.begin() as connection:
            if engine.dialect.name == "postgresql":
                connection.execute(
                    text(
                        "TRUNCATE "
                        + ", ".join('"' + t.name + '"' for t in Base.metadata.sorted_tables)
                        + " RESTART IDENTITY CASCADE"
                    )
                )
            else:
                for table in reversed(Base.metadata.sorted_tables):
                    connection.execute(table.delete())
        seed()


if __name__ == "__main__":
    main()
