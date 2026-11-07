"""Synchronous SQLAlchemy boundary; PostgreSQL is the deployment database."""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from reconflow.config import settings


class Base(DeclarativeBase):
    pass


def now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


engine = create_engine(settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
