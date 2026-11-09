"""The one check service. Every channel calls this, so verdicts are identical everywhere."""

from __future__ import annotations

import hashlib
import re

from confam_contract.serialize import verdict_to_json
from confam_contract.verdict import Verdict
from confam_engine import check_notice

from .record import RecordHolder
from .store import CheckStore


def content_hash(text: str, lang: str) -> str:
    normal = re.sub(r"\s+", " ", text).strip().casefold()
    return hashlib.sha256(f"{lang}\n{normal}".encode("utf-8")).hexdigest()


class CheckService:
    def __init__(self, holder: RecordHolder, store: CheckStore) -> None:
        self.holder = holder
        self.store = store

    def check_text(self, text: str, lang: str = "en") -> Verdict:
        record = self.holder.record
        key = content_hash(text, lang)

        cached = self.store.get_by_hash(key)
        if cached is not None:
            # Cache hit: only supersession (and record_as_of) is re-checked (rule 2).
            verdict = self._refresh(cached)
            self.store.put(verdict, content_hash=key)
            return verdict

        verdict = check_notice(text, record.notices, record_as_of=record.record_as_of, lang=lang)
        self.store.put(verdict, content_hash=key)
        return verdict

    def refreshed(self, verdict: Verdict) -> Verdict:
        """For the public page: always serve the current supersession state."""
        return self._refresh(verdict)

    def _refresh(self, verdict: Verdict) -> Verdict:
        record = self.holder.record
        if verdict.verdict.value != "confirmed" or verdict.notice is None:
            return verdict
        notice = record.get(verdict.notice.id)
        if notice is None:
            return verdict
        payload = verdict_to_json(verdict)
        payload["superseded_by"] = (
            {"id": notice.superseded_by.id, "published": notice.superseded_by.published}
            if notice.superseded_by
            else None
        )
        payload["record_as_of"] = record.record_as_of.isoformat()
        return Verdict.model_validate(payload)
