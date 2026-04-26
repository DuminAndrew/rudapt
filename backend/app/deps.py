from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import ApiKey, User
from app.security import decode_token
from app.services.api_keys import hash_key

bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(creds.credentials)
        if payload.get("type") != "access":
            raise ValueError("wrong token type")
        user_id = UUID(payload["sub"])
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from e

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return user


async def get_user_by_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    from app.services.rate_limit import check as rl_check

    if not x_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "X-API-Key header required")
    key = await db.scalar(select(ApiKey).where(ApiKey.key_hash == hash_key(x_api_key)))
    if key is None or key.revoked_at is not None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or revoked api key")

    allowed, _ = rl_check(str(key.id), key.rate_limit_per_min)
    if not allowed:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "rate limit exceeded")

    user = await db.get(User, key.user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    key.last_used_at = datetime.now(timezone.utc)
    await db.commit()
    return user
