"""Tests for packages/contract/verdict.schema.json.

Every cross-field rule has a positive and a negative case. These tests validate
against the schema itself, because the generated types describe shape only.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "verdict.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)

NOTICE = {
    "id": "SEC-2026-114",
    "title": "Voter registration deadline",
    "published": "2026-09-03",
    "url": "https://sec.example/notices/SEC-2026-114",
}


def make(**overrides):
    """A valid `confirmed` verdict, with overrides applied on top."""
    base = {
        "code": "K7Q2M9XA",
        "verdict": "confirmed",
        "reason": None,
        "lang": "en",
        "checked_at": "2026-11-05T14:02:00+01:00",
        "record_as_of": "2026-11-05T13:40:00+01:00",
        "notice": copy.deepcopy(NOTICE),
        "superseded_by": None,
        "changes": [],
        "conflicts": [],
    }
    base.update(overrides)
    return base


CONFLICT = {"kind": "date", "copy": "15th", "official": "14th", "quote": "Deadline is 14th."}
REPLACE = {"op": "replace", "kind": "date", "official": "14th", "copy": "15th"}


def valid(doc) -> bool:
    return VALIDATOR.is_valid(doc)


def test_schema_itself_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


# --- the baseline shapes ---------------------------------------------------


def test_confirmed_example_is_valid():
    assert valid(make())


def test_claude_md_altered_example_with_box_is_valid():
    doc = make(
        verdict="altered",
        changes=[{**REPLACE, "box": [0.21, 0.46, 0.08, 0.03]}],
    )
    assert valid(doc)


@pytest.mark.parametrize("verdict", ["confirmed", "altered", "not_official", "partial", "cannot_confirm"])
def test_verdict_enum_accepts_only_known_values(verdict):
    assert VALIDATOR.is_valid(make(verdict="nonsense")) is False
    # each known value is exercised in its own rule tests below; here just the enum
    errors = [e for e in VALIDATOR.iter_errors(make(verdict=verdict)) if list(e.absolute_path) == ["verdict"]]
    assert errors == []


@pytest.mark.parametrize("lang", ["en", "pcm", "ha", "yo", "ig"])
def test_lang_accepts_five_languages(lang):
    assert valid(make(lang=lang))


def test_lang_rejects_others():
    assert not valid(make(lang="fr"))


# --- check code ------------------------------------------------------------


@pytest.mark.parametrize("code", ["K7Q2M9XA", "23456789", "ZZZZZZZZ"])
def test_code_accepts_alphabet(code):
    assert valid(make(code=code))


@pytest.mark.parametrize(
    "code",
    [
        "K7Q2M9X",  # 7 chars
        "K7Q2M9XAB",  # 9 chars
        "K7Q2-M9XA",  # display form is not the stored form
        "K7Q2M9X0",  # zero
        "K7Q2M9XO",  # letter O
        "K7Q2M9X1",  # one
        "K7Q2M9XI",  # letter I
        "K7Q2M9XL",  # letter L
        "k7q2m9xa",  # lower case
        "",
    ],
)
def test_code_rejects_bad_codes(code):
    assert not valid(make(code=code))


# --- no scores (rule 4) ----------------------------------------------------


@pytest.mark.parametrize("field", ["confidence", "score", "percent", "grade", "probability"])
def test_top_level_score_fields_are_rejected(field):
    assert not valid(make(**{field: 0.9}))


def test_score_field_inside_change_is_rejected():
    assert not valid(make(verdict="altered", changes=[{**REPLACE, "confidence": 0.9}]))


# --- reason ----------------------------------------------------------------


@pytest.mark.parametrize("reason", ["unclear", "not_in_record", "no_fact", "line_missing"])
def test_cannot_confirm_requires_a_reason(reason):
    notice = None if reason in ("not_in_record", "no_fact") else copy.deepcopy(NOTICE)
    assert valid(make(verdict="cannot_confirm", reason=reason, notice=notice))


def test_cannot_confirm_with_null_reason_is_rejected():
    assert not valid(make(verdict="cannot_confirm", reason=None))


def test_reason_must_be_null_for_other_verdicts():
    assert not valid(make(verdict="confirmed", reason="unclear"))
    assert not valid(make(verdict="partial", reason="line_missing"))


def test_unknown_reason_is_rejected():
    assert not valid(make(verdict="cannot_confirm", reason="looks_fake"))


# --- notice nullability ----------------------------------------------------


@pytest.mark.parametrize("reason", ["not_in_record", "no_fact"])
def test_notice_may_be_null_for_not_in_record_and_no_fact(reason):
    assert valid(make(verdict="cannot_confirm", reason=reason, notice=None))


def test_notice_is_required_for_line_missing():
    assert not valid(make(verdict="cannot_confirm", reason="line_missing", notice=None))
    assert valid(make(verdict="cannot_confirm", reason="line_missing", notice=copy.deepcopy(NOTICE)))


def test_unclear_may_have_a_null_notice_when_nothing_could_be_read():
    """Approved contract change: a photo with no usable text has no notice to point at."""
    assert valid(make(verdict="cannot_confirm", reason="unclear", notice=None))
    assert valid(make(verdict="cannot_confirm", reason="unclear", notice=copy.deepcopy(NOTICE)))


@pytest.mark.parametrize("verdict", ["confirmed", "altered", "partial", "not_official"])
def test_unclear_does_not_loosen_the_notice_rule_for_other_verdicts(verdict):
    extra = {"conflicts": [CONFLICT]} if verdict == "not_official" else {}
    assert not valid(make(verdict=verdict, notice=None, **extra))


@pytest.mark.parametrize("verdict", ["confirmed", "altered", "partial"])
def test_notice_is_required_for_other_verdicts(verdict):
    assert not valid(make(verdict=verdict, notice=None))


def test_not_official_requires_notice():
    assert not valid(make(verdict="not_official", conflicts=[CONFLICT], notice=None))


# --- superseded_by ---------------------------------------------------------

SUPERSEDED = {
    "id": "SEC-2026-140",
    "published": "2026-10-09",
    "url": "https://sec.example/notices/SEC-2026-140",
    "title": "Simulated Electoral Commission: revised voter registration deadline",
    "changes": [{"op": "replace", "kind": "date", "official": "28th November", "copy": "14th November"}],
}


def test_superseded_by_allowed_on_confirmed():
    assert valid(make(superseded_by=SUPERSEDED))


@pytest.mark.parametrize("verdict", ["altered", "partial"])
def test_superseded_by_rejected_on_altered_and_partial(verdict):
    assert not valid(make(verdict=verdict, superseded_by=SUPERSEDED))


def test_superseded_by_rejected_on_not_official():
    assert not valid(make(verdict="not_official", conflicts=[CONFLICT], superseded_by=SUPERSEDED))


def test_superseded_by_rejected_on_cannot_confirm():
    assert not valid(
        make(verdict="cannot_confirm", reason="unclear", superseded_by=SUPERSEDED)
    )


@pytest.mark.parametrize("missing", ["id", "published", "url", "title", "changes"])
def test_superseded_by_requires_all_five_fields(missing):
    partial = {k: v for k, v in SUPERSEDED.items() if k != missing}
    assert not valid(make(superseded_by=partial))


def test_superseded_by_rejects_extra_fields():
    assert not valid(make(superseded_by={**SUPERSEDED, "confidence": 1}))


def test_superseded_by_changes_may_be_empty():
    assert valid(make(superseded_by={**SUPERSEDED, "changes": []}))


def test_superseded_by_change_rejects_a_box():
    change = {"op": "replace", "kind": "date", "official": "28th", "copy": "14th", "box": [0, 0, 1, 1]}
    assert not valid(make(superseded_by={**SUPERSEDED, "changes": [change]}))


def test_superseded_by_change_insert_has_null_official_and_delete_null_copy():
    insert = {"op": "insert", "kind": "text", "official": None, "copy": "old words"}
    delete = {"op": "delete", "kind": "text", "official": "new words", "copy": None}
    assert valid(make(superseded_by={**SUPERSEDED, "changes": [insert, delete]}))
    bad_insert = {**insert, "official": "x"}
    bad_delete = {**delete, "copy": "x"}
    assert not valid(make(superseded_by={**SUPERSEDED, "changes": [bad_insert]}))
    assert not valid(make(superseded_by={**SUPERSEDED, "changes": [bad_delete]}))


def test_superseded_by_change_replace_needs_both_strings():
    for field in ("official", "copy"):
        change = {"op": "replace", "kind": "date", "official": "28th", "copy": "14th", field: None}
        assert not valid(make(superseded_by={**SUPERSEDED, "changes": [change]}))


@pytest.mark.parametrize("kind", ["date", "time", "weekday", "number", "money", "link", "phone", "negation", "text"])
def test_superseded_by_change_kind_accepts_the_nine_kinds(kind):
    change = {"op": "replace", "kind": kind, "official": "a", "copy": "b"}
    assert valid(make(superseded_by={**SUPERSEDED, "changes": [change]}))


def test_superseded_by_change_kind_rejects_others():
    change = {"op": "replace", "kind": "name", "official": "a", "copy": "b"}
    assert not valid(make(superseded_by={**SUPERSEDED, "changes": [change]}))


# --- conflicts (both directions) ------------------------------------------


def test_not_official_with_conflicts_is_valid():
    assert valid(make(verdict="not_official", conflicts=[CONFLICT]))


def test_not_official_with_empty_conflicts_is_rejected():
    assert not valid(make(verdict="not_official", conflicts=[]))


@pytest.mark.parametrize("verdict", ["confirmed", "altered", "partial"])
def test_conflicts_must_be_empty_for_other_verdicts(verdict):
    assert not valid(make(verdict=verdict, conflicts=[CONFLICT]))


def test_conflicts_must_be_empty_for_cannot_confirm():
    assert not valid(
        make(verdict="cannot_confirm", reason="not_in_record", notice=None, conflicts=[CONFLICT])
    )


@pytest.mark.parametrize("kind", ["date", "link", "money"])
def test_conflict_kind_accepts_three_kinds(kind):
    assert valid(make(verdict="not_official", conflicts=[{**CONFLICT, "kind": kind}]))


def test_conflict_kind_rejects_other_kinds():
    assert not valid(make(verdict="not_official", conflicts=[{**CONFLICT, "kind": "phone"}]))


# --- changes: box ----------------------------------------------------------


def test_box_is_optional():
    assert valid(make(verdict="altered", changes=[REPLACE]))


def test_box_with_four_numbers_in_range_is_valid():
    assert valid(make(verdict="altered", changes=[{**REPLACE, "box": [0, 0, 1, 1]}]))


@pytest.mark.parametrize(
    "box",
    [
        [0.1, 0.2, 0.3],  # too short
        [0.1, 0.2, 0.3, 0.4, 0.5],  # too long
        [-0.1, 0.2, 0.3, 0.4],  # below 0
        [0.1, 0.2, 0.3, 1.1],  # above 1
        [0.1, 0.2, "0.3", 0.4],  # not a number
        None,  # null is not "absent"
    ],
)
def test_bad_box_is_rejected(box):
    assert not valid(make(verdict="altered", changes=[{**REPLACE, "box": box}]))


# --- changes: official / copy nullability by op ----------------------------


def test_insert_has_null_official_and_string_copy():
    change = {"op": "insert", "kind": "text", "official": None, "copy": "extra words"}
    assert valid(make(verdict="altered", changes=[change]))


def test_insert_with_non_null_official_is_rejected():
    change = {"op": "insert", "kind": "text", "official": "x", "copy": "extra words"}
    assert not valid(make(verdict="altered", changes=[change]))


def test_insert_with_null_copy_is_rejected():
    change = {"op": "insert", "kind": "text", "official": None, "copy": None}
    assert not valid(make(verdict="altered", changes=[change]))


def test_delete_has_null_copy_and_string_official():
    change = {"op": "delete", "kind": "negation", "official": "not", "copy": None}
    assert valid(make(verdict="altered", changes=[change]))


def test_delete_with_non_null_copy_is_rejected():
    change = {"op": "delete", "kind": "negation", "official": "not", "copy": "x"}
    assert not valid(make(verdict="altered", changes=[change]))


def test_delete_with_null_official_is_rejected():
    change = {"op": "delete", "kind": "negation", "official": None, "copy": None}
    assert not valid(make(verdict="altered", changes=[change]))


@pytest.mark.parametrize("field", ["official", "copy"])
def test_replace_requires_both_strings(field):
    change = {**REPLACE, field: None}
    assert not valid(make(verdict="altered", changes=[change]))


@pytest.mark.parametrize("field", ["official", "copy"])
def test_official_and_copy_keys_must_be_present(field):
    change = {k: v for k, v in REPLACE.items() if k != field}
    assert not valid(make(verdict="altered", changes=[change]))


# --- changes: kind and op enums -------------------------------------------


@pytest.mark.parametrize(
    "kind", ["date", "time", "weekday", "number", "money", "link", "phone", "negation", "text"]
)
def test_change_kind_accepts_nine_kinds(kind):
    assert valid(make(verdict="altered", changes=[{**REPLACE, "kind": kind}]))


@pytest.mark.parametrize("kind", ["name", "place", "other", "Date", ""])
def test_change_kind_rejects_others(kind):
    assert not valid(make(verdict="altered", changes=[{**REPLACE, "kind": kind}]))


def test_change_op_rejects_unknown():
    assert not valid(make(verdict="altered", changes=[{**REPLACE, "op": "move"}]))


# --- timestamps ------------------------------------------------------------


@pytest.mark.parametrize("field", ["checked_at", "record_as_of"])
@pytest.mark.parametrize("value", ["2026-11-05T14:02:00Z", "2026-11-05T14:02:00+01:00"])
def test_timestamps_accept_offsets(field, value):
    assert valid(make(**{field: value}))


@pytest.mark.parametrize("field", ["checked_at", "record_as_of"])
@pytest.mark.parametrize("value", ["2026-11-05T14:02:00", "2026-11-05", "yesterday"])
def test_timestamps_require_an_offset(field, value):
    assert not valid(make(**{field: value}))
