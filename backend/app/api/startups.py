from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models import Startup, User
from app.schemas.startup import StartupListOut, StartupOut

router = APIRouter(prefix="/api/startups", tags=["startups"])


@router.get("", response_model=StartupListOut)
async def list_startups(
    q: str | None = Query(None, description="full-text по name/tagline"),
    source: str | None = Query(None, pattern="^(producthunt|yc|crunchbase)$"),
    category: str | None = Query(None),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StartupListOut:
    stmt = select(Startup)
    count_stmt = select(func.count()).select_from(Startup)

    if q:
        like = f"%{q.lower()}%"
        cond = (func.lower(Startup.name).like(like)) | (func.lower(Startup.tagline).like(like))
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if source:
        stmt = stmt.where(Startup.source == source)
        count_stmt = count_stmt.where(Startup.source == source)
    if category:
        stmt = stmt.where(Startup.categories.any(category))
        count_stmt = count_stmt.where(Startup.categories.any(category))

    total = await db.scalar(count_stmt) or 0
    rows = (
        await db.scalars(
            stmt.order_by(Startup.launched_at.desc().nulls_last()).limit(limit).offset(offset)
        )
    ).all()
    return StartupListOut(
        items=[StartupOut.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{startup_id}", response_model=StartupOut)
async def get_startup(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StartupOut:
    from uuid import UUID

    s = await db.get(Startup, UUID(startup_id))
    if not s:
        from fastapi import HTTPException

        raise HTTPException(404, "startup not found")
    return StartupOut.model_validate(s)
