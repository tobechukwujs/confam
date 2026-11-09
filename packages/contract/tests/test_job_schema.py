"""packages/contract/job.schema.json: the progress of a photo check."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "job.schema.json").read_text(encoding="utf-8"))
V = Draft202012Validator(SCHEMA)
JOB_ID = "Xk3-9_abcDEF1234567"


def job(**kw):
    base = {"job_id": JOB_ID, "status": "working", "stage": "reading_1", "code": None}
    base.update(kw)
    return base


def ok(doc) -> bool:
    return V.is_valid(doc)


def test_schema_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("stage", ["queued", "reading_1", "reading_2", "comparing"])
def test_working_stages(stage):
    assert ok(job(stage=stage))


def test_done_needs_a_code_and_the_done_stage():
    assert ok(job(status="done", stage="done", code="K7Q2M9XA"))
    assert not ok(job(status="done", stage="done", code=None))
    assert not ok(job(status="done", stage="comparing", code="K7Q2M9XA"))


def test_code_only_when_done():
    assert not ok(job(status="working", code="K7Q2M9XA"))
    assert not ok(job(status="failed", stage="failed", code="K7Q2M9XA"))


def test_failed_has_the_failed_stage_and_no_code():
    assert ok(job(status="failed", stage="failed"))
    assert not ok(job(status="failed", stage="reading_1"))


def test_working_cannot_have_a_done_or_failed_stage():
    assert not ok(job(status="working", stage="done"))
    assert not ok(job(status="working", stage="failed"))


@pytest.mark.parametrize("bad", ["short", "has space 12345678", "x" * 65, "", "bad/char/1234567890"])
def test_job_id_shape(bad):
    assert not ok(job(job_id=bad))


@pytest.mark.parametrize("code", ["K7Q2M9X0", "K7Q2-M9XA", "k7q2m9xa", "K7Q2M9X"])
def test_a_bad_code_is_rejected(code):
    assert not ok(job(status="done", stage="done", code=code))


@pytest.mark.parametrize("field", ["progress", "percent", "confidence", "score", "eta"])
def test_no_progress_numbers_or_scores(field):
    assert not ok(job(**{field: 50}))
