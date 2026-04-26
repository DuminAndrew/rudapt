"""Public API v1 — авторизация через X-API-Key, rate-limit на ключ."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_user_by_api_key
from app.models import Report, Startup, User
from app.schemas.report import (
    GeneratePlanIn,
    ReportListOut,
    ReportOut,
    ReportWithStartup,
)
from app.schemas.startup import StartupListOut, StartupOut
from app.services.queue import enqueue_or_run
from app.workers.generate import generate_report

router = APIRouter(prefix="/api/v1", tags=["public-api-v1"])


@router.get("/startups", response_model=StartupListOut)
async def v1_list_startups(
    q: str | None = None,
    source: str | None = Query(None, pattern="^(producthunt|yc|crunchbase)$"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_user_by_api_key),
) -> StartupListOut:
    stmt = select(Startup)
    cnt = select(func.count()).select_from(Startup)
    if q:
        like = f"%{q.lower()}%"
        cond = func.lower(Startup.name).like(like) | func.lower(Startup.tagline).like(like)
        stmt = stmt.where(cond)
        cnt = cnt.where(cond)
    if source:
        stmt = stmt.where(Startup.source == source)
        cnt = cnt.where(Startup.source == source)
    total = await db.scalar(cnt) or 0
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


@router.post("/generate-plan", response_model=ReportOut, status_code=202)
async def v1_generate(
    payload: GeneratePlanIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_by_api_key),
) -> ReportOut:
    startup = await db.get(Startup, payload.startup_id)
    if startup is None:
        raise HTTPException(404, "startup not found")
    report = Report(
        user_id=user.id,
        startup_id=startup.id,
        region=payload.region.strip(),
        status="pending",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    async def _inproc(rid: str):
        await generate_report({}, rid)

    await enqueue_or_run("generate_report", str(report.id), fallback_fn=_inproc)
    return ReportOut.model_validate(report)


@router.get("/reports/{report_id}", response_model=ReportWithStartup)
async def v1_get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_by_api_key),
) -> ReportWithStartup:
    r = await db.get(Report, report_id)
    if r is None or r.user_id != user.id:
        raise HTTPException(404, "report not found")
    out = ReportWithStartup.model_validate(r)
    s = await db.get(Startup, r.startup_id)
    if s is not None:
        out.startup = StartupOut.model_validate(s)
    return out


@router.get("/reports", response_model=ReportListOut)
async def v1_list_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_by_api_key),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ReportListOut:
    total = await db.scalar(
        select(func.count()).select_from(Report).where(Report.user_id == user.id)
    ) or 0
    rows = (
        await db.scalars(
            select(Report)
            .where(Report.user_id == user.id)
            .order_by(Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return ReportListOut(items=[ReportOut.model_validate(r) for r in rows], total=total)
