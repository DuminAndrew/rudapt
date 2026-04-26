"""Обёртка над Anthropic / OpenAI с prompt caching и JSON-режимом."""
from __future__ import annotations

import json
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.services.prompt import SYSTEM_PROMPT


@dataclass
class LLMResult:
    content: dict
    model: str
    prompt_tokens: int
    completion_tokens: int


def _coerce_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
async def _call_anthropic(user_message: str) -> LLMResult:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model=settings.LLM_MODEL_ANTHROPIC,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")
    usage = msg.usage
    return LLMResult(
        content=_coerce_json(text),
        model=settings.LLM_MODEL_ANTHROPIC,
        prompt_tokens=getattr(usage, "input_tokens", 0) or 0,
        completion_tokens=getattr(usage, "output_tokens", 0) or 0,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
async def _call_openai(user_message: str) -> LLMResult:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    completion = await client.chat.completions.create(
        model=settings.LLM_MODEL_OPENAI,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )
    text = completion.choices[0].message.content or "{}"
    usage = completion.usage
    return LLMResult(
        content=_coerce_json(text),
        model=settings.LLM_MODEL_OPENAI,
        prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )


async def generate_business_plan(user_message: str) -> LLMResult:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _call_anthropic(user_message)
    if provider == "openai" and settings.OPENAI_API_KEY:
        return await _call_openai(user_message)
    if settings.ANTHROPIC_API_KEY:
        return await _call_anthropic(user_message)
    if settings.OPENAI_API_KEY:
        return await _call_openai(user_message)
    raise RuntimeError("No LLM provider configured: set ANTHROPIC_API_KEY or OPENAI_API_KEY")
