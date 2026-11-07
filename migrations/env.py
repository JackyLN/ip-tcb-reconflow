"""Alembic runtime migration configuration."""

from alembic import context

from reconflow import models  # noqa: F401
from reconflow.db import Base, engine

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
