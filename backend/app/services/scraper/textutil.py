"""Очистка HTML/whitespace из текстовых полей RSS-фидов."""
from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_text(s: str | None, *, max_len: int | None = None) -> str | None:
    if not s:
        return None
    no_tags = _TAG_RE.sub(" ", s)
    unescaped = html.unescape(no_tags)
    collapsed = _WS_RE.sub(" ", unescaped).strip()
    if not collapsed:
        return None
    if max_len and len(collapsed) > max_len:
        collapsed = collapsed[: max_len - 1].rstrip() + "…"
    return collapsed
