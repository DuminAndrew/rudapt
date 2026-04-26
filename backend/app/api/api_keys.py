from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models import ApiKey, User
from app.schemas.api_key import ApiKeyCreated, ApiKeyCreateIn, ApiKeyOut
from app.services.api_keys import generate_key

router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyOut])
async def list_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApiKey]:
    rows = (
        await db.scalars(
            select(ApiKey)
            .where(ApiKey.user_id == user.id)
            .order_by(ApiKey.created_at.desc())
        )
    ).all()
    return list(rows)


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_key(
    payload: ApiKeyCreateIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiKeyCreated:
    plaintext, prefix, digest = generate_key()
    key = ApiKey(
        user_id=user.id,
        name=payload.name,
        prefix=prefix,
        key_hash=digest,
        rate_limit_per_min=payload.rate_limit_per_min,
    )
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return ApiKeyCreated(
        id=key.id,
        name=key.name,
        prefix=key.prefix,
        rate_limit_per_min=key.rate_limit_per_min,
        created_at=key.created_at,
        last_used_at=key.last_used_at,
        revoked_at=key.revoked_at,
        plaintext=plaintext,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    key = await db.get(ApiKey, key_id)
    if key is None or key.user_id != user.id:
        raise HTTPException(404, "key not found")
    if key.revoked_at is None:
        key.revoked_at = datetime.now(timezone.utc)
        await db.commit()
