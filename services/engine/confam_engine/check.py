from __future__ import annotations

import secrets
from collections.abc import Sequence
from datetime import datetime, timezone

from confam_contract.verdict import Verdict

from .evaluate import Outcome, evaluate
from .model import OfficialNotice

# Same alphabet as the contract: no 0, O, 1, I, L.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def new_check_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


def _notice_dict(n: OfficialNotice | None) -> dict | None:
    if n is None:
        return None
    return {"id": n.id, "title": n.title, "published": n.published, "url": n.url}


def verdict_from_outcome(
    outcome: Outcome, *, lang: str, record_as_of: datetime, now: datetime | None = None
) -> Verdict:
    return Verdict.model_validate(
        {
            "code": new_check_code(),
            "verdict": outcome.verdict,
            "reason": outcome.reason,
            "lang": lang,
            "checked_at": (now or datetime.now(timezone.utc)).isoformat(),
            "record_as_of": record_as_of.isoformat(),
            "notice": _notice_dict(outcome.notice),
            "superseded_by": outcome.superseded_by,
            "changes": [d.to_photo_change() for d in outcome.changes],
            "conflicts": outcome.conflicts,
        }
    )


def check_notice(
    text: str,
    record: Sequence[OfficialNotice],
    *,
    record_as_of: datetime,
    lang: str = "en",
    now: datetime | None = None,
) -> Verdict:
    """Check pasted text against the signed record. Rules decide the verdict (rule 3)."""
    return verdict_from_outcome(evaluate(text, record), lang=lang, record_as_of=record_as_of, now=now)
