"""Password hashing and JWT handling."""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings

_BCRYPT_ROUNDS = 12

# File logger — writes to <project_root>/debug_auth.log
_log_path = Path(__file__).resolve().parents[2] / "debug_auth.log"
_fh = logging.FileHandler(_log_path, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
dbg = logging.getLogger("auth_debug")
dbg.setLevel(logging.DEBUG)
if not dbg.handlers:
    dbg.addHandler(_fh)


def hash_password(password: str) -> str:
    dbg.debug("[security] hash_password called")
    dbg.debug("[security] password length=%d (redacted)", len(password))
    result = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(_BCRYPT_ROUNDS)).decode("utf-8")
    dbg.debug("[security] hash result=%s...", result[:20] if result else "")
    return result


def verify_password(plain: str, hashed: str) -> bool:
    dbg.debug("[security] verify_password called")
    dbg.debug("[security] plain password length=%d (redacted)", len(plain))
    try:
        result = bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
    dbg.debug("[security] verify result=%s", result)
    return result


def create_access_token(sub: str, email: str | None = None) -> str:
    return _create_token(
        sub=sub,
        token_type="access",
        email=email,
        expires_delta=timedelta(minutes=settings.jwt_access_expire_minutes),
    )


def create_refresh_token(sub: str, email: str | None = None) -> str:
    return _create_token(
        sub=sub,
        token_type="refresh",
        email=email,
        expires_delta=timedelta(days=settings.jwt_refresh_expire_days),
    )


def _create_token(
    sub: str,
    token_type: str,
    email: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=15))
    payload: dict[str, Any] = {
        "sub": sub,
        "type": token_type,
        "iat": now,
        "exp": expire,
    }
    if email:
        payload["email"] = email
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None


def get_access_token_expiry_seconds() -> int:
    return settings.jwt_access_expire_minutes * 60
