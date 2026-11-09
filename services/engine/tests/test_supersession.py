"""Rule 2: replaced notices are flagged.

A match to a superseded notice sets `superseded_by`. The UI must never show a
plain green tick for it. This test must never be weakened or deleted.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, Replacement, check_notice

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] / "packages" / "contract" / "verdict.schema.json").read_text(
        encoding="utf-8"
    )
)
VALIDATOR = Draft202012Validator(SCHEMA)

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
RECORD_AS_OF = datetime(2026, 11, 8, 11, 30, tzinfo=timezone.utc)

# Fictional "Simulated Electoral Commission" content only (rule 9).
TEXT = "The Simulated Electoral Commission announces that voter registration closes on 14th November."
OLD = OfficialNotice(
    id="SEC-2026-114",
    title="Simulated Electoral Commission: voter registration deadline",
    published="2026-09-03",
    url="https://sec.example/notices/SEC-2026-114",
    text=TEXT,
    superseded_by=Replacement(id="SEC-2026-140", published="2026-10-09"),
)
CURRENT = OfficialNotice(
    id="SEC-2026-140",
    title="Simulated Electoral Commission: revised registration deadline",
    published="2026-10-09",
    url="https://sec.example/notices/SEC-2026-140",
    text="The Simulated Electoral Commission announces that voter registration closes on 28th November.",
)


def _check(text, record):
    return check_notice(text, record, record_as_of=RECORD_AS_OF, lang="en", now=NOW)


def test_match_to_replaced_notice_sets_superseded_by():
    verdict = _check(TEXT, [OLD, CURRENT])
    assert verdict.verdict.value == "confirmed"
    assert verdict.superseded_by is not None
    assert verdict.superseded_by.id == "SEC-2026-140"
    assert str(verdict.superseded_by.published) == "2026-10-09"
    assert verdict.notice is not None and verdict.notice.id == "SEC-2026-114"


def test_match_to_current_notice_has_no_superseded_by():
    verdict = _check(CURRENT.text, [OLD, CURRENT])
    assert verdict.verdict.value == "confirmed"
    assert verdict.superseded_by is None


def test_replaced_match_is_valid_against_the_contract_schema():
    payload = _check(TEXT, [OLD, CURRENT]).model_dump(mode="json", by_alias=True)
    errors = list(VALIDATOR.iter_errors(payload))
    assert errors == [], [e.message for e in errors]
