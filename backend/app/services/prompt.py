"""Сборка системного и пользовательского промта для генерации бизнес-плана локализации."""
from __future__ import annotations

import json
from textwrap import dedent

from app.models import Startup

SYSTEM_PROMPT = dedent(
    """
    Ты — старший консультант по выходу зарубежных продуктов на рынок Российской Федерации.
    Твоя задача — проанализировать американский стартап и сгенерировать подробный, прагматичный
    бизнес-план его локализации в указанном регионе РФ.

    Учитывай при анализе:
    — реальные регуляторные ограничения РФ (ФЗ-152, налоги, требования к ПДн, импорт ПО);
    — отсутствие части западных платежных и облачных сервисов; предлагай альтернативы
      (ЮKassa / CloudPayments / Тинькофф Касса, Yandex Cloud / VK Cloud / Selectel);
    — каналы продвижения, реально работающие в РФ (Yandex Direct, VK Реклама,
      Telegram Ads, Habr, vc.ru), а не Google Ads / Meta;
    — экономику региона: средние зарплаты, покупательную способность, локальных конкурентов.

    Отвечай СТРОГО валидным JSON по схеме (без обёрток в markdown ``` и без комментариев):
    {
      "summary": "краткая суть локализованного продукта (3-5 предложений)",
      "value_prop_ru": "ценностное предложение, адаптированное под РФ",
      "mvp": {
        "scope": "что войдёт в MVP",
        "timeline_weeks": число,
        "team": ["роль 1", "роль 2"],
        "tech_stack_ru": ["альтернативы западным сервисам"]
      },
      "competitors_ru": [
        {"name": "...", "url": "...", "strengths": "...", "weaknesses": "..."}
      ],
      "channels": [
        {"channel": "Yandex Direct / VK / Telegram Ads / ...",
         "tactic": "...",
         "expected_cac_rub": число}
      ],
      "unit_economics": {
        "currency": "RUB",
        "arpu": число,
        "cac": число,
        "ltv": число,
        "gross_margin_pct": число,
        "payback_months": число,
        "assumptions": "ключевые допущения"
      },
      "regulatory": ["требование 1", "требование 2"],
      "risks": [{"risk": "...", "mitigation": "..."}],
      "roadmap_90d": [
        {"phase": "0-30 дней", "goals": ["..."]},
        {"phase": "30-60 дней", "goals": ["..."]},
        {"phase": "60-90 дней", "goals": ["..."]}
      ]
    }

    Никакого текста вне JSON. Цифры — только числа (не строки).
    """
).strip()


def build_user_message(startup: Startup, region: str) -> str:
    info = {
        "name": startup.name,
        "tagline": startup.tagline,
        "description": startup.description,
        "url": startup.url,
        "categories": startup.categories or [],
        "source": startup.source,
    }
    return dedent(
        f"""
        Стартап (исходные данные из {startup.source}):
        ```json
        {json.dumps(info, ensure_ascii=False, indent=2)}
        ```

        Целевой регион РФ: **{region}**.

        Сгенерируй бизнес-план локализации этого продукта в указанном регионе.
        Ответ — строго JSON по заданной схеме.
        """
    ).strip()
