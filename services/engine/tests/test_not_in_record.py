"""Rule 1: "Not in our record" is never "fake".

No match and no conflicting official fact returns `cannot_confirm` with reason
`not_in_record`. Never `not_official`. This test must never be weakened or deleted.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, check_notice, new_check_code

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] / "packages" / "contract" / "verdict.schema.json").read_text(
        encoding="utf-8"
    )
)
VALIDATOR = Draft202012Validator(SCHEMA)

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
RECORD_AS_OF = datetime(2026, 11, 8, 11, 30, tzinfo=timezone.utc)

# Fictional "Simulated Electoral Commission" content only (rule 9).
UNRELATED = OfficialNotice(
    id="SEC-2026-114",
    title="Simulated Electoral Commission: voter registration deadline",
    published="2026-09-03",
    url="https://sec.example/notices/SEC-2026-114",
    text="The Simulated Electoral Commission announces that voter registration closes on 14th November.",
)
RUMOUR = "Collect your new ballot cards at the market square on Sunday."


def _check(record):
    return check_notice(RUMOUR, record, record_as_of=RECORD_AS_OF, lang="en", now=NOW)


def test_empty_record_is_cannot_confirm_not_in_record():
    verdict = _check([])
    assert verdict.verdict.value == "cannot_confirm"
    assert verdict.reason.value == "not_in_record"
    assert verdict.verdict.value != "not_official"


def test_unrelated_record_is_cannot_confirm_not_in_record():
    verdict = _check([UNRELATED])
    assert verdict.verdict.value == "cannot_confirm"
    assert verdict.reason.value == "not_in_record"


def test_no_conflicts_and_no_notice_on_not_in_record():
    verdict = _check([UNRELATED])
    assert verdict.conflicts == []
    assert verdict.notice is None
    assert verdict.superseded_by is None


def test_result_is_valid_against_the_contract_schema():
    for record in ([], [UNRELATED]):
        payload = _check(record).model_dump(mode="json", by_alias=True)
        errors = list(VALIDATOR.iter_errors(payload))
        assert errors == [], [e.message for e in errors]


def test_check_code_uses_the_contract_alphabet():
    alphabet = set("23456789ABCDEFGHJKMNPQRSTUVWXYZ")
    for _ in range(200):
        code = new_check_code()
        assert len(code) == 8
        assert set(code) <= alphabet
