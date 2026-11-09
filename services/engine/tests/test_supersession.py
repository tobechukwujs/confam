"""Rule 2: replaced notices are flagged.

A match to a superseded notice sets `superseded_by`, with the replacing notice's id,
date, url, title and the changes between the two. The UI must never show a plain green
tick for it. This test must never be weakened or deleted.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from confam_engine import (
    OfficialNotice,
    RecordError,
    Replacement,
    check_notice,
    supersession_for,
)

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] / "packages" / "contract" / "verdict.schema.json").read_text(
        encoding="utf-8"
    )
)
VALIDATOR = Draft202012Validator(SCHEMA)

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
RECORD_AS_OF = datetime(2026, 11, 8, 11, 30, tzinfo=timezone.utc)

# Fictional "Simulated Electoral Commission" content only (rule 9).
OLD_TEXT = "The Simulated Electoral Commission announces that voter registration closes on 14th November. Register only at https://register.sec.example. Registration is free."
NEW_TEXT = "The Simulated Electoral Commission announces that voter registration now closes on 28th November. Register only at https://register.sec.example. Registration is free."
NEWEST_TEXT = "The Simulated Electoral Commission announces that voter registration now closes on 5th December. Register only at https://register.sec.example. Registration is free."

OLD = OfficialNotice(
    id="SEC-2026-114",
    title="Simulated Electoral Commission: voter registration deadline",
    published="2026-09-03",
    url="https://sec.example/notices/SEC-2026-114",
    text=OLD_TEXT,
    superseded_by=Replacement(id="SEC-2026-140", published="2026-10-09"),
)
CURRENT = OfficialNotice(
    id="SEC-2026-140",
    title="Simulated Electoral Commission: revised voter registration deadline",
    published="2026-10-09",
    url="https://sec.example/notices/SEC-2026-140",
    text=NEW_TEXT,
)
NEWEST = OfficialNotice(
    id="SEC-2026-150",
    title="Simulated Electoral Commission: voter registration extended",
    published="2026-11-02",
    url="https://sec.example/notices/SEC-2026-150",
    text=NEWEST_TEXT,
)


def _check(text, record):
    return check_notice(text, record, record_as_of=RECORD_AS_OF, lang="en", now=NOW)


def test_match_to_replaced_notice_sets_superseded_by():
    verdict = _check(OLD_TEXT, [OLD, CURRENT])
    assert verdict.verdict.value == "confirmed"
    assert verdict.notice is not None and verdict.notice.id == "SEC-2026-114"
    sup = verdict.superseded_by
    assert sup is not None
    assert sup.id == "SEC-2026-140"
    assert str(sup.published) == "2026-10-09"
    assert sup.url == "https://sec.example/notices/SEC-2026-140"
    assert sup.title == "Simulated Electoral Commission: revised voter registration deadline"


def test_superseded_by_lists_what_changed_old_to_new():
    sup = _check(OLD_TEXT, [OLD, CURRENT]).superseded_by
    assert sup is not None
    got = {(c.op.value, c.kind.value, c.official, c.copy_) for c in sup.changes}
    # official = value in the NEW notice, copy = value in the OLD notice
    assert ("replace", "date", "28th November", "14th November") in got
    assert ("delete", "text", "now", None) in got
    assert len(got) == 2


def test_match_to_current_notice_has_no_superseded_by():
    verdict = _check(NEW_TEXT, [OLD, CURRENT])
    assert verdict.verdict.value == "confirmed"
    assert verdict.superseded_by is None


def test_chain_of_replacements_points_at_the_newest_notice():
    mid = replace(CURRENT, superseded_by=Replacement(id="SEC-2026-150", published="2026-11-02"))
    sup = _check(OLD_TEXT, [OLD, mid, NEWEST]).superseded_by
    assert sup is not None and sup.id == "SEC-2026-150"
    got = {(c.kind.value, c.official, c.copy_) for c in sup.changes}
    assert ("date", "5th December", "14th November") in got


def test_dangling_replacement_is_a_record_error():
    with pytest.raises(RecordError):
        supersession_for(OLD, [OLD])  # SEC-2026-140 is not in the record


def test_replacement_cycle_is_a_record_error():
    a = replace(OLD, superseded_by=Replacement(id="SEC-2026-140", published="2026-10-09"))
    b = replace(CURRENT, superseded_by=Replacement(id="SEC-2026-114", published="2026-09-03"))
    with pytest.raises(RecordError):
        supersession_for(a, [a, b])


def test_supersession_for_a_current_notice_is_none():
    assert supersession_for(CURRENT, [OLD, CURRENT]) is None


def test_replaced_match_is_valid_against_the_contract_schema():
    payload = _check(OLD_TEXT, [OLD, CURRENT]).model_dump(mode="json", by_alias=True)
    errors = list(VALIDATOR.iter_errors(payload))
    assert errors == [], [e.message for e in errors]
