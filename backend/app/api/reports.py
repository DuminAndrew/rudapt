from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models import Report, Startup, User
from app.schemas.report import (
    GeneratePlanIn,
    ReportListOut,
    ReportOut,
    ReportWithStartup,
)
from app.services.queue import enqueue_or_run
from app.workers.generate import generate_report

router = APIRouter(prefix="/api", tags=["reports"])


@router.post("/generate-plan", response_model=ReportOut, status_code=status.HTTP_202_ACCEPTED)
async def generate_plan(
    payload: GeneratePlanIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportOut:
    startup = await db.get(Startup, payload.startup_id)
    if startup is None:
        raise HTTPException(404, "startup not found")

    regions = payload.normalized_regions()
    if not regions:
        raise HTTPException(400, "region or regions[] required")

    report = Report(
        user_id=user.id,
        startup_id=startup.id,
        region=regions[0],
        regions=regions if len(regions) > 1 else None,
        status="pending",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    async def _inproc(rid: str):
        await generate_report({}, rid)

    await enqueue_or_run("generate_report", str(report.id), fallback_fn=_inproc)
    return ReportOut.model_validate(report)


@router.get("/reports", response_model=ReportListOut)
async def list_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
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


@router.get("/reports/{report_id}", response_model=ReportWithStartup)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportWithStartup:
    report = await db.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(404, "report not found")
    startup = await db.get(Startup, report.startup_id)
    out = ReportWithStartup.model_validate(report)
    if startup is not None:
        from app.schemas.startup import StartupOut

        out.startup = StartupOut.model_validate(startup)
    return out
