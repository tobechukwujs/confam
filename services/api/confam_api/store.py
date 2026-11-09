"""In-memory check store.

Rule 7: only the verdict (notice-level facts) and a one-way content hash are kept.
The pasted text, images and phone numbers never reach this store. Checks expire
after 30 days. TODO(ARCHITECTURE.md): replace with the PostgreSQL `checks` table.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from confam_contract.verdict import Verdict
from confam_contract.serialize import verdict_to_json

TTL = timedelta(days=30)


@dataclass
class Entry:
    verdict: Verdict
    content_hash: str | None
    expires_at: datetime | None  # None = sample, never expires


class CheckStore:
    def __init__(self) -> None:
        self._entries: dict[str, Entry] = {}
        self._by_hash: dict[str, str] = {}
        self._lock = threading.Lock()

    def put(self, verdict: Verdict, *, content_hash: str | None = None, permanent: bool = False,
            now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        with self._lock:
            self._entries[verdict.code] = Entry(
                verdict=verdict,
                content_hash=content_hash,
                expires_at=None if permanent else now + TTL,
            )
            if content_hash:
                self._by_hash[content_hash] = verdict.code

    def get(self, code: str, now: datetime | None = None) -> Verdict | None:
        now = now or datetime.now(timezone.utc)
        with self._lock:
            entry = self._entries.get(code)
            if entry is None or (entry.expires_at is not None and entry.expires_at <= now):
                return None
            return entry.verdict

    def get_by_hash(self, content_hash: str) -> Verdict | None:
        with self._lock:
            code = self._by_hash.get(content_hash)
        return self.get(code) if code else None

    def expire_all(self, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        with self._lock:
            gone = [c for c, e in self._entries.items() if e.expires_at is not None and e.expires_at <= now]
            for code in gone:
                entry = self._entries.pop(code)
                if entry.content_hash:
                    self._by_hash.pop(entry.content_hash, None)
            return len(gone)

    def dump(self) -> list[dict]:
        """Everything held, for tests that prove no personal data is kept."""
        with self._lock:
            return [
                {
                    "verdict": verdict_to_json(e.verdict),
                    "content_hash": e.content_hash,
                    "expires_at": e.expires_at.isoformat() if e.expires_at else None,
                }
                for e in self._entries.values()
            ]
