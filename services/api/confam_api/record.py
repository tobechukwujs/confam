from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from confam_engine import OfficialNotice, RecordError, Replacement, Signature, latest_successor


@dataclass
class Record:
    notices: list[OfficialNotice]
    record_as_of: datetime

    def get(self, notice_id: str) -> OfficialNotice | None:
        return next((n for n in self.notices if n.id == notice_id), None)


@dataclass
class RecordHolder:
    """Mutable pointer to the current record, so tests (and later the signed-record
    reload) can swap it without rebuilding the app."""

    record: Record = field(default=None)  # type: ignore[assignment]


def _signatures(notice_id: str, raw: list[dict]) -> tuple[Signature, ...]:
    """Rule 5: two people sign every record entry, one first and one second, never the same person."""
    sigs = tuple(Signature(reviewer=s["reviewer"], role=s["role"], signed_at=s["signed_at"]) for s in raw)
    if len(sigs) != 2 or sorted(s.role for s in sigs) != ["first", "second"]:
        raise RecordError(f"{notice_id} needs exactly one first and one second signature")
    if sigs[0].reviewer == sigs[1].reviewer:
        raise RecordError(f"{notice_id} was signed twice by the same reviewer")
    return tuple(sorted(sigs, key=lambda s: s.role != "first"))


def load_record(path: Path) -> Record:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    notices = [
        OfficialNotice(
            id=n["id"],
            title=n["title"],
            published=n["published"],
            url=n["url"],
            text=n["text"],
            lang=n.get("lang", "en"),
            superseded_by=(
                Replacement(id=n["superseded_by"]["id"], published=n["superseded_by"]["published"])
                if n.get("superseded_by")
                else None
            ),
            signatures=_signatures(n["id"], n.get("signatures", [])),
        )
        for n in data["notices"]
    ]
    for notice in notices:  # a dangling or circular replacement is a broken record
        latest_successor(notice, notices)
    return Record(notices=notices, record_as_of=datetime.fromisoformat(data["record_as_of"]))
