"""Tests for the generated Pydantic models. Needs `pnpm contract:gen` to have run."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from confam_contract.verdict import Verdict

EXAMPLE = {
    "code": "K7Q2M9XA",
    "verdict": "altered",
    "reason": None,
    "lang": "en",
    "checked_at": "2026-11-05T14:02:00+01:00",
    "record_as_of": "2026-11-05T13:40:00+01:00",
    "notice": {
        "id": "SEC-2026-114",
        "title": "Voter registration deadline",
        "published": "2026-09-03",
        "url": "https://sec.example/notices/SEC-2026-114",
    },
    "superseded_by": None,
    "changes": [
        {"op": "replace", "kind": "date", "official": "14th", "copy": "15th", "box": [0.21, 0.46, 0.08, 0.03]}
    ],
    "conflicts": [],
}


def test_example_round_trips():
    # `copy` clashes with BaseModel.copy, so the generator names the field `copy_`
    # with alias `copy`. Always serialise with by_alias=True.
    model = Verdict.model_validate(EXAMPLE)
    again = Verdict.model_validate(model.model_dump(mode="json", by_alias=True))
    assert again == model


def test_absent_box_is_omitted_not_null_and_payload_validates():
    import json
    from pathlib import Path

    from jsonschema import Draft202012Validator

    from confam_contract.serialize import verdict_to_json

    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "verdict.schema.json").read_text(encoding="utf-8")
    )
    change = {"op": "replace", "kind": "date", "official": "14th", "copy": "15th"}
    payload = verdict_to_json(Verdict.model_validate({**EXAMPLE, "changes": [change]}))
    assert "box" not in payload["changes"][0]
    assert payload["changes"][0]["copy"] == "15th"
    assert list(Draft202012Validator(schema).iter_errors(payload)) == []
    # and a present box is kept
    with_box = verdict_to_json(Verdict.model_validate(EXAMPLE))
    assert with_box["changes"][0]["box"] == [0.21, 0.46, 0.08, 0.03]


def test_dump_by_alias_uses_contract_field_name_copy():
    dumped = Verdict.model_validate(EXAMPLE).model_dump(mode="json", by_alias=True)
    change = dumped["changes"][0]
    assert "copy" in change and "copy_" not in change


@pytest.mark.parametrize("code", ["K7Q2M9X0", "K7Q2M9X", "K7Q2-M9XA"])
def test_bad_code_raises(code):
    with pytest.raises(ValidationError):
        Verdict.model_validate({**EXAMPLE, "code": code})


def test_extra_field_raises():
    with pytest.raises(ValidationError):
        Verdict.model_validate({**EXAMPLE, "confidence": 0.9})


def test_unknown_verdict_raises():
    with pytest.raises(ValidationError):
        Verdict.model_validate({**EXAMPLE, "verdict": "fake"})
