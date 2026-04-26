from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode("utf-8")[:72], h.encode("utf-8"))
    except Exception:
        return False


def _create_token(sub: str, ttl: timedelta, kind: str) -> str:
    payload = {
        "sub": sub,
        "type": kind,
        "exp": datetime.now(timezone.utc) + ttl,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_access_token(user_id: UUID) -> str:
    return _create_token(str(user_id), timedelta(minutes=settings.ACCESS_TOKEN_TTL_MIN), "access")


def create_refresh_token(user_id: UUID) -> str:
    return _create_token(str(user_id), timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS), "refresh")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as e:
        raise ValueError("invalid token") from e
