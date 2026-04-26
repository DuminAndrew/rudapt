"""ARQ-воркер: генерация бизнес-плана через LLM."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from app.db import SessionLocal
from app.models import Report, Startup
from app.services.llm import generate_business_plan
from app.services.markdown import render_multi_region_md, render_plan_md
from app.services.prompt import build_user_message

log = logging.getLogger(__name__)


async def generate_report(ctx, report_id: str) -> dict:
    rid = UUID(report_id)
    async with SessionLocal() as db:
        report = await db.get(Report, rid)
        if report is None:
            return {"ok": False, "error": "report not found"}
        startup = await db.get(Startup, report.startup_id)
        if startup is None:
            report.status = "failed"
            report.error = "startup not found"
            await db.commit()
            return {"ok": False, "error": "startup not found"}

        report.status = "running"
        await db.commit()

        try:
            regions = list(report.regions or [])
            if not regions:
                regions = [report.region]
            user_msg = build_user_message(startup, regions)
            result = await generate_business_plan(user_msg)

            report.status = "done"
            report.model = result.model
            report.content = result.content
            if len(regions) > 1:
                report.content_md = render_multi_region_md(result.content, startup.name)
            else:
                report.content_md = render_plan_md(result.content, startup.name, regions[0])
            report.prompt_tokens = result.prompt_tokens
            report.completion_tokens = result.completion_tokens
            report.finished_at = datetime.now(timezone.utc)
            await db.commit()
            return {"ok": True, "report_id": report_id}
        except Exception as e:
            log.exception("generate_report failed for %s", report_id)
            report.status = "failed"
            report.error = str(e)[:1990]
            report.finished_at = datetime.now(timezone.utc)
            await db.commit()
            return {"ok": False, "error": str(e)}
