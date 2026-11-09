from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from confam_engine import OfficialNotice, Replacement


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


def load_record(path: Path) -> Record:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    notices = [
        OfficialNotice(
            id=n["id"],
            title=n["title"],
            published=n["published"],
            url=n["url"],
            text=n["text"],
            superseded_by=(
                Replacement(id=n["superseded_by"]["id"], published=n["superseded_by"]["published"])
                if n.get("superseded_by")
                else None
            ),
        )
        for n in data["notices"]
    ]
    return Record(notices=notices, record_as_of=datetime.fromisoformat(data["record_as_of"]))
