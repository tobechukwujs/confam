"""The fictional record the evaluation runs against: fixtures/sec-sim/notices.json (the fictional
Simulated Electoral Commission), loaded as engine objects."""

from __future__ import annotations

import json
from pathlib import Path

from confam_engine import OfficialNotice, Replacement, Signature

ROOT = Path(__file__).resolve().parents[1]
NOTICES_JSON = ROOT / "fixtures" / "sec-sim" / "notices.json"


def load_record(path: Path = NOTICES_JSON) -> tuple[list[OfficialNotice], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for n in data["notices"]:
        sup = n.get("superseded_by")
        out.append(
            OfficialNotice(
                id=n["id"], title=n["title"], published=n["published"], url=n["url"], text=n["text"],
                lang=n.get("lang", "en"),
                superseded_by=Replacement(sup["id"], sup["published"]) if sup else None,
                signatures=tuple(Signature(s["reviewer"], s["role"], s["signed_at"]) for s in n.get("signatures", [])),
            )
        )
    return out, data
