from __future__ import annotations

import re
import secrets
from collections.abc import Sequence
from datetime import datetime, timezone

from confam_contract.verdict import Verdict

from .model import OfficialNotice
from .supersession import supersession_for

# Same alphabet as the contract: no 0, O, 1, I, L.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def new_check_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def check_notice(
    text: str,
    record: Sequence[OfficialNotice],
    *,
    record_as_of: datetime,
    lang: str = "en",
    now: datetime | None = None,
) -> Verdict:
    """STUB: an exact (whitespace and case-insensitive) match, or no match.

    - Exact match: `confirmed`, with `superseded_by` set if the notice was replaced (rule 2).
    - Anything else: `cannot_confirm` / `not_in_record` (rule 1). A near-match is NOT
      compared here, so an altered copy is reported as not in the record, never as fake.

    TODO: port the real comparison engine (diff, meaning rules, allow-list, explain).
    It never returns altered, partial or not_official on its own.
    """
    checked_at = (now or datetime.now(timezone.utc)).isoformat()
    base = {
        "code": new_check_code(),
        "lang": lang,
        "checked_at": checked_at,
        "record_as_of": record_as_of.isoformat(),
        "changes": [],
        "conflicts": [],
    }

    needle = _normalise(text)
    for notice in record:
        if _normalise(notice.text) == needle:
            return Verdict.model_validate(
                {
                    **base,
                    "verdict": "confirmed",
                    "reason": None,
                    "notice": {
                        "id": notice.id,
                        "title": notice.title,
                        "published": notice.published,
                        "url": notice.url,
                    },
                    "superseded_by": supersession_for(notice, record),
                }
            )

    return Verdict.model_validate(
        {
            **base,
            "verdict": "cannot_confirm",
            "reason": "not_in_record",
            "notice": None,
            "superseded_by": None,
        }
    )
