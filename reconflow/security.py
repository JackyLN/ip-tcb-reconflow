"""Server-side authentication sessions and explicit role/CSRF gates."""

import hashlib
import secrets
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import HTTPException, Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from reconflow.db import now
from reconflow.models import LoginAttempt, LoginSession, User
from reconflow.services.audit import append

hasher = PasswordHasher()


def csrf_token(request: Request) -> str:
    if "csrf" not in request.session:
        request.session["csrf"] = secrets.token_urlsafe(32)
    return request.session["csrf"]


def csrf(request: Request, value: str) -> None:
    if not secrets.compare_digest(request.session.get("csrf", ""), value) or not value:
        raise HTTPException(403, "Invalid CSRF token; refresh the page")


def current_user(request: Request, db: Session) -> User:
    token = request.session.get("sid", "")
    session = db.get(LoginSession, hashlib.sha256(token.encode()).hexdigest()) if token else None
    if not session or session.expires_at < now():
        raise HTTPException(401, "Please sign in")
    return db.get(User, session.user_id)


def require(user: User, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(403, "Your role cannot perform this action")


def login(request: Request, db: Session, email: str, password: str) -> bool:
    """DB-backed per-client bucket, no credentials recorded. Five attempts per 5 minutes."""
    bucket = hashlib.sha256(
        (request.client.host if request.client else "unknown").encode()
    ).hexdigest()
    attempts = db.scalar(
        select(func.count())
        .select_from(LoginAttempt)
        .where(
            LoginAttempt.bucket == bucket, LoginAttempt.created_at > now() - timedelta(minutes=5)
        )
    )
    if attempts >= 5:
        raise HTTPException(429, "Too many sign-in attempts; wait five minutes")
    db.add(LoginAttempt(bucket=bucket))
    user = db.scalar(select(User).where(User.email == email.lower()))
    try:
        # Fixed dummy hash prevents missing-user fast path; initialized once below.
        valid = hasher.verify(user.password_hash if user else DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        valid = False
    if not user or not valid:
        append(db, "anonymous", "login.failed", "authentication")
        return False
    db.execute(delete(LoginAttempt).where(LoginAttempt.bucket == bucket))
    token = secrets.token_urlsafe(48)
    db.add(
        LoginSession(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            user_id=user.id,
            expires_at=now() + timedelta(hours=8),
        )
    )
    request.session.clear()
    request.session.update(sid=token, csrf=secrets.token_urlsafe(32))
    append(db, user.id, "login.succeeded", "authentication")
    return True


DUMMY_HASH = hasher.hash(secrets.token_urlsafe(32))
