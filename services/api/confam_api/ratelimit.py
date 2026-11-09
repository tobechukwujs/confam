"""Per-IP rate limit on salted IP hashes (the raw IP is never kept).

In-memory sliding window for now. TODO(ARCHITECTURE.md): move to Redis and add the
per-hashed-sender limit when channels arrive.
"""

from __future__ import annotations

import hashlib
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, limit: int, salt: str, window: float = 60.0) -> None:
        self.limit, self.salt, self.window = limit, salt, window
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, ip: str) -> bool:
        key = hashlib.sha256(f"{self.salt}:{ip}".encode()).hexdigest()
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True
