"""Рендер JSON-плана в человекочитаемый Markdown для UI и экспорта."""
from __future__ import annotations


def _list(items: list, fmt) -> str:
    return "\n".join(fmt(i) for i in items) if items else "_не указано_"


def render_plan_md(plan: dict, startup_name: str, region: str) -> str:
    lines: list[str] = [
        f"# Бизнес-план локализации: **{startup_name}** → {region}",
        "",
        "## Резюме",
        plan.get("summary", "—"),
        "",
        "## Ценностное предложение для РФ",
        plan.get("value_prop_ru", "—"),
        "",
        "## MVP",
    ]
    mvp = plan.get("mvp") or {}
    lines += [
        f"- **Объём:** {mvp.get('scope', '—')}",
        f"- **Сроки:** {mvp.get('timeline_weeks', '—')} нед.",
        f"- **Команда:** {', '.join(mvp.get('team', [])) or '—'}",
        f"- **Стек / сервисы РФ:** {', '.join(mvp.get('tech_stack_ru', [])) or '—'}",
        "",
        "## Конкуренты в РФ",
        _list(
            plan.get("competitors_ru", []),
            lambda c: f"- **{c.get('name','—')}** — {c.get('url','')}\n  - Сильные: {c.get('strengths','—')}\n  - Слабые: {c.get('weaknesses','—')}",
        ),
        "",
        "## Каналы продвижения",
        _list(
            plan.get("channels", []),
            lambda c: f"- **{c.get('channel','—')}** — {c.get('tactic','')} (CAC ≈ {c.get('expected_cac_rub','—')} ₽)",
        ),
        "",
        "## Юнит-экономика",
    ]
    ue = plan.get("unit_economics") or {}
    lines += [
        f"- **ARPU:** {ue.get('arpu','—')} {ue.get('currency','RUB')}",
        f"- **CAC:** {ue.get('cac','—')}",
        f"- **LTV:** {ue.get('ltv','—')}",
        f"- **Маржа:** {ue.get('gross_margin_pct','—')}%",
        f"- **Окупаемость:** {ue.get('payback_months','—')} мес.",
        f"- **Допущения:** {ue.get('assumptions','—')}",
        "",
        "## Регуляторика",
        _list(plan.get("regulatory", []), lambda x: f"- {x}"),
        "",
        "## Риски",
        _list(
            plan.get("risks", []),
            lambda r: f"- **{r.get('risk','—')}** — _митигация:_ {r.get('mitigation','—')}",
        ),
        "",
        "## Roadmap (90 дней)",
        _list(
            plan.get("roadmap_90d", []),
            lambda p: f"### {p.get('phase','—')}\n" + "\n".join(f"- {g}" for g in p.get("goals", [])),
        ),
    ]
    return "\n".join(lines)
