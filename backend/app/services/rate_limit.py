"""In-memory rate limiter (sliding window per-key per-minute).

Для production с несколькими процессами лучше Redis-based. Для dev / single-instance — этого достаточно.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def check(key: str, limit_per_min: int) -> tuple[bool, int]:
    """Возвращает (allowed, remaining). Пишет timestamp в bucket если allowed."""
    now = time.monotonic()
    window_start = now - 60.0
    bucket = _BUCKETS[key]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= limit_per_min:
        return False, 0
    bucket.append(now)
    return True, max(0, limit_per_min - len(bucket))
