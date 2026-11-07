"""Isolated SQLite unit/API tests; PostgreSQL concurrency has a separate smoke check."""

import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mkdtemp(prefix="reconflow-test-") + "/test.db"
os.environ["SESSION_SECRET"] = "test-only-secret-no-production-value-0123456789"
os.environ["DEMO_MODE"] = "true"
os.environ["COOKIE_SECURE"] = "false"
os.environ["LLM_API_KEY"] = ""
os.environ["LLM_MODEL"] = ""
import re

import pytest
from fastapi.testclient import TestClient

from reconflow.db import Base, SessionLocal, engine
from reconflow.main import app
from reconflow.models import Control, Provider, User
from reconflow.security import hasher


@pytest.fixture(autouse=True)
def isolated_db():
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        db.add(Control(id=1))
        db.add(Provider(name="SyntheticPay", fee_bps=200, tolerance=0))
        for role in ("analyst", "supervisor", "auditor", "admin", "manager"):
            db.add(
                User(
                    email=f"{role}@reconflow.demo",
                    password_hash=hasher.hash("test-password"),
                    role=role,
                )
            )
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def token(client, path="/"):
    page = client.get(path)
    return re.search(r'name="csrf_value" value="([^"]+)"', page.text).group(1)


def sign_in(client, role="analyst"):
    csrf = token(client, "/login")
    response = client.post(
        "/login",
        data={"csrf_value": csrf, "email": f"{role}@reconflow.demo", "password": "test-password"},
    )
    assert response.status_code == 200
    return token(client)
