"""Public record pages: GET /v1/record and GET /v1/record/{id}. Rule 5 mirrored in the fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from confam_api.app import create_app
from confam_api.record import load_record
from confam_api.settings import Settings
from confam_engine import RecordError

ROOT = Path(__file__).resolve().parents[3]
RECORD = load_record(ROOT / "fixtures/sec-sim/notices.json")


def client() -> TestClient:
    return TestClient(create_app(settings=Settings(seed_samples=False), record=RECORD))


def test_list_returns_every_notice_with_replacement_info():
    body = client().get("/v1/record").json()
    ids = [n["id"] for n in body["notices"]]
    assert ids == [n.id for n in RECORD.notices]
    by_id = {n["id"]: n for n in body["notices"]}
    assert by_id["SEC-2026-114"]["superseded_by"] == {"id": "SEC-2026-140", "published": "2026-10-09"}
    assert by_id["SEC-2026-140"]["superseded_by"] is None
    assert body["record_as_of"].startswith("2026-")
    assert all({"id", "title", "published", "lang", "superseded_by"} <= set(n) for n in body["notices"])


def test_entry_returns_the_exact_signed_text():
    notice = RECORD.get("SEC-2026-140")
    body = client().get("/v1/record/SEC-2026-140").json()
    assert body["text"] == notice.text  # byte for byte, never reworded
    assert body["title"] == notice.title
    assert body["published"] == "2026-10-09"
    assert body["lang"] == "en"
    assert body["url"] == notice.url
    assert body["superseded_by"] is None


def test_entry_of_a_replaced_notice_says_what_replaced_it():
    body = client().get("/v1/record/SEC-2026-114").json()
    assert body["superseded_by"] == {"id": "SEC-2026-140", "published": "2026-10-09"}


@pytest.mark.parametrize("notice_id", [n.id for n in RECORD.notices])
def test_every_entry_has_two_signatures_from_two_different_reviewers(notice_id):
    sigs = client().get(f"/v1/record/{notice_id}").json()["signatures"]
    assert [s["role"] for s in sigs] == ["first", "second"]
    assert len({s["reviewer"] for s in sigs}) == 2
    assert all(s["signed_at"].startswith("2026-") for s in sigs)
    assert all("sample" in s["reviewer"].lower() for s in sigs), "fixture reviewers are labelled as samples"


@pytest.mark.parametrize("bad", ["SEC-0000-000", "SEC 2026", "x" * 200])
def test_unknown_or_malformed_id_is_404(bad):
    assert client().get(f"/v1/record/{bad}").status_code == 404


def test_record_responses_carry_no_scores():
    text = json.dumps(client().get("/v1/record/SEC-2026-114").json()).lower()
    for word in ("confidence", "score", "percent", "grade", "probability"):
        assert word not in text


def _write(tmp_path, signatures):
    path = tmp_path / "notices.json"
    path.write_text(
        json.dumps(
            {
                "record_as_of": "2026-11-08T09:00:00+01:00",
                "notices": [
                    {
                        "id": "SEC-2026-114", "title": "t", "published": "2026-09-03",
                        "url": "https://sec.example/n", "text": "x", "lang": "en",
                        "superseded_by": None, "signatures": signatures,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def sig(name, role):
    return {"reviewer": name, "role": role, "signed_at": "2026-09-04T10:00:00+01:00"}


def test_load_record_accepts_two_different_reviewers(tmp_path):
    load_record(_write(tmp_path, [sig("Reviewer A (sample)", "first"), sig("Reviewer B (sample)", "second")]))


@pytest.mark.parametrize(
    "signatures",
    [
        [],
        [sig("Reviewer A (sample)", "first")],
        [sig("Reviewer A (sample)", "first"), sig("Reviewer A (sample)", "second")],  # same person twice (rule 5)
        [sig("Reviewer A (sample)", "first"), sig("Reviewer B (sample)", "first")],  # no second signature
        [sig("A", "first"), sig("B", "second"), sig("C", "second")],
    ],
)
def test_load_record_rejects_bad_signatures(tmp_path, signatures):
    with pytest.raises(RecordError):
        load_record(_write(tmp_path, signatures))
