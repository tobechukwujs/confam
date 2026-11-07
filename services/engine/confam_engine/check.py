from __future__ import annotations

import re
import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from confam_contract.verdict import Verdict

# Same alphabet as the contract: no 0, O, 1, I, L.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


@dataclass(frozen=True)
class OfficialNotice:
    id: str
    title: str
    published: str  # YYYY-MM-DD
    url: str
    text: str


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
    """STUB: handles only "no match, no conflict".

    A copy that matches a record notice needs the real comparison engine, so the
    stub refuses rather than guess. It never returns not_official on its own.
    """
    needle = _normalise(text)
    for notice in record:
        if _normalise(notice.text) == needle:
            raise NotImplementedError(
                "TODO: matched notices need the real engine (to be ported into services/engine)"
            )

    checked_at = (now or datetime.now(timezone.utc)).isoformat()
    return Verdict.model_validate(
        {
            "code": new_check_code(),
            "verdict": "cannot_confirm",
            "reason": "not_in_record",
            "lang": lang,
            "checked_at": checked_at,
            "record_as_of": record_as_of.isoformat(),
            "notice": None,
            "superseded_by": None,
            "changes": [],
            "conflicts": [],
        }
    )
