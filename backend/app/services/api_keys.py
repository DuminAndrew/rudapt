"""Генерация, хеширование и проверка API-ключей."""
from __future__ import annotations

import hashlib
import secrets

KEY_PREFIX = "rdpt_"


def generate_key() -> tuple[str, str, str]:
    """Возвращает (plaintext, prefix, sha256_hash)."""
    body = secrets.token_urlsafe(32)
    plaintext = f"{KEY_PREFIX}{body}"
    prefix = plaintext[: len(KEY_PREFIX) + 6]  # rdpt_xxxxxx
    digest = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
    return plaintext, prefix, digest


def hash_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
