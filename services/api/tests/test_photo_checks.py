"""Photo checks over the API: raw image body in, {job_id} out, real stages, verdict at the end.

Readers are fakes here, so these tests need no Tesseract. The image is processed in memory only
(rule 7) and the job never exposes the picture or any score (rule 4)."""

from __future__ import annotations

import io
import json
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from PIL import Image

from confam_api.app import create_app
from confam_api.record import load_record
from confam_api.settings import Settings
from confam_engine.ocr import Reading, Word
from confam_engine.ocr.imageio import MAX_BYTES

ROOT = Path(__file__).resolve().parents[3]
RECORD = load_record(ROOT / "fixtures/sec-sim/notices.json")
JOB_SCHEMA = Draft202012Validator(json.loads((ROOT / "packages/contract/job.schema.json").read_text(encoding="utf-8")))
VERDICT_SCHEMA = Draft202012Validator(json.loads((ROOT / "packages/contract/verdict.schema.json").read_text(encoding="utf-8")))
NEW_TEXT = RECORD.get("SEC-2026-140").text
OLD_TEXT = RECORD.get("SEC-2026-114").text


def png(w=120, h=80, mode="RGB") -> bytes:
    buf = io.BytesIO()
    Image.new(mode, (w, h), "white").save(buf, "PNG")
    return buf.getvalue()


def reading(text: str) -> Reading:
    return Reading([Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04) for i, w in enumerate(text.split())])


class FakeReader:
    def __init__(self, name, text, gate=None, started=None, boom=False):
        self.name, self.text, self.gate, self.started, self.boom = name, text, gate, started, boom

    def read(self, image):
        if self.started:
            self.started.set()
        if self.gate:
            assert self.gate.wait(5), "test never released the reader"
        if self.boom:
            raise RuntimeError("reader exploded: secret internal detail")
        return reading(self.text)


def make(readers, **settings):
    app = create_app(settings=Settings(seed_samples=False, **settings), record=RECORD, readers=readers)
    return TestClient(app), app


def upload(client, data=None, content_type="image/png", lang="en"):
    return client.post(
        f"/v1/checks?lang={lang}", content=png() if data is None else data, headers={"Content-Type": content_type}
    )


def wait_done(client, job_id, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        body = client.get(f"/v1/checks/{job_id}").json()
        errors = [e.message for e in JOB_SCHEMA.iter_errors(body)]
        assert errors == [], errors
        if body["status"] != "working":
            return body
        time.sleep(0.02)
    raise AssertionError("job did not finish")


def same(text):
    return (FakeReader("a", text), FakeReader("b", text))


# --- the happy path ---------------------------------------------------------


def test_upload_returns_202_with_only_a_job_id():
    client, _ = make(same(NEW_TEXT))
    res = upload(client)
    assert res.status_code == 202
    assert set(res.json()) == {"job_id"}
    assert len(res.json()["job_id"]) >= 16


def test_job_finishes_with_a_code_that_opens_the_verdict():
    client, _ = make(same(NEW_TEXT))
    job = wait_done(client, upload(client).json()["job_id"])
    assert job["status"] == "done" and job["stage"] == "done" and job["code"]
    verdict = client.get(f"/v1/verdicts/{job['code']}").json()
    assert verdict["verdict"] == "confirmed"
    assert [e.message for e in VERDICT_SCHEMA.iter_errors(verdict)] == []


def test_a_replaced_notice_in_a_photo_is_flagged():
    client, _ = make(same(OLD_TEXT))
    job = wait_done(client, upload(client).json()["job_id"])
    verdict = client.get(f"/v1/verdicts/{job['code']}").json()
    assert verdict["verdict"] == "confirmed" and verdict["superseded_by"]["id"] == "SEC-2026-140"  # rule 2


def test_an_edit_both_readings_see_gives_altered_with_a_box():
    edited = NEW_TEXT.replace("28th November", "29th November")
    client, _ = make(same(edited))
    job = wait_done(client, upload(client).json()["job_id"])
    verdict = client.get(f"/v1/verdicts/{job['code']}").json()
    assert verdict["verdict"] == "altered"
    date = next(c for c in verdict["changes"] if c["kind"] == "date")
    assert date["copy"] == "29th November" and date["official"] == "28th November"
    assert len(date["box"]) == 4 and all(0 <= v <= 1 for v in date["box"])
    assert [e.message for e in VERDICT_SCHEMA.iter_errors(verdict)] == []


def test_readings_that_disagree_give_cannot_confirm_unclear():
    edited = NEW_TEXT.replace("28th November", "29th November")
    client, _ = make((FakeReader("a", edited), FakeReader("b", NEW_TEXT)))
    job = wait_done(client, upload(client).json()["job_id"])
    verdict = client.get(f"/v1/verdicts/{job['code']}").json()
    assert verdict["verdict"] == "cannot_confirm" and verdict["reason"] == "unclear"


def test_the_language_in_the_query_is_carried_on_the_verdict():
    client, _ = make(same(NEW_TEXT))
    job = wait_done(client, upload(client, lang="yo").json()["job_id"])
    assert client.get(f"/v1/verdicts/{job['code']}").json()["lang"] == "yo"


# --- real stages --------------------------------------------------------------


def test_the_job_reports_the_real_stage_it_is_on():
    g1, g2 = threading.Event(), threading.Event()
    s1, s2 = threading.Event(), threading.Event()
    client, _ = make((FakeReader("a", NEW_TEXT, gate=g1, started=s1), FakeReader("b", NEW_TEXT, gate=g2, started=s2)))
    job_id = upload(client).json()["job_id"]
    assert s1.wait(5)
    assert client.get(f"/v1/checks/{job_id}").json() | {} == {"job_id": job_id, "status": "working", "stage": "reading_1", "code": None}
    g1.set()
    assert s2.wait(5)
    assert client.get(f"/v1/checks/{job_id}").json()["stage"] == "reading_2"
    g2.set()
    assert wait_done(client, job_id)["status"] == "done"


# --- upload checks -------------------------------------------------------------


@pytest.mark.parametrize(
    "data,ctype",
    [
        (b"just some text", "image/png"),
        (b"%PDF-1.4 ...", "application/pdf"),
        (b"GIF89a....", "image/gif"),
        (png(), "text/plain"),  # declared type must say image too
        (b"", "image/png"),
    ],
)
def test_wrong_type_is_415_with_a_plain_message(data, ctype):
    client, _ = make(same(NEW_TEXT))
    res = upload(client, data=data, content_type=ctype)
    assert res.status_code == 415
    assert "JPG, PNG or WebP" in res.json()["detail"]


def test_a_picture_over_the_size_limit_is_413():
    client, _ = make(same(NEW_TEXT))
    res = upload(client, data=b"\x89PNG\r\n\x1a\n" + b"0" * (MAX_BYTES + 10))
    assert res.status_code == 413


def test_a_huge_picture_in_a_tiny_file_is_refused_before_decoding():
    buf = io.BytesIO()
    Image.new("L", (6000, 6000), 255).save(buf, "PNG")
    client, _ = make(same(NEW_TEXT))
    assert upload(client, data=buf.getvalue()).status_code == 413


def test_a_picture_cut_off_in_the_header_is_refused_up_front():
    client, _ = make(same(NEW_TEXT))
    assert upload(client, data=png()[:20]).status_code == 415


def test_a_picture_with_a_good_header_but_a_broken_body_fails_the_job_plainly():
    import random

    buf = io.BytesIO()
    rng = random.Random(1)
    noisy = Image.frombytes("RGB", (200, 200), bytes(rng.randrange(256) for _ in range(200 * 200 * 3)))
    noisy.save(buf, "PNG")
    data = bytearray(buf.getvalue())
    mid = len(data) // 2
    data[mid : mid + 64] = b"\x00" * 64  # damage the compressed pixels, keep the header
    client, _ = make(same(NEW_TEXT))
    res = upload(client, data=bytes(data))
    assert res.status_code == 202
    job_id = res.json()["job_id"]
    assert wait_done(client, job_id) == {"job_id": job_id, "status": "failed", "stage": "failed", "code": None}

def test_unknown_language_is_422():
    client, _ = make(same(NEW_TEXT))
    assert upload(client, lang="fr").status_code == 422


def test_text_checks_still_work_on_the_same_route():
    client, _ = make(same(NEW_TEXT))
    res = client.post("/v1/checks", json={"text": NEW_TEXT})
    assert res.status_code == 200 and res.json()["verdict"] == "confirmed"


# --- failure, availability, expiry ---------------------------------------------


def test_a_reader_that_crashes_fails_the_job_without_leaking_details():
    client, _ = make((FakeReader("a", "x", boom=True), FakeReader("b", "x")))
    job_id = upload(client).json()["job_id"]
    job = wait_done(client, job_id)
    assert job == {"job_id": job_id, "status": "failed", "stage": "failed", "code": None}
    assert "secret" not in json.dumps(job)


def test_no_readers_means_photo_checks_are_unavailable_but_text_works():
    client, _ = make(None)
    res = upload(client)
    assert res.status_code == 503
    assert "paste the text" in res.json()["detail"].lower()
    assert client.get("/health").json() == {"status": "ok", "photo_checks": False}
    assert client.post("/v1/checks", json={"text": "hello there"}).status_code == 200


def test_health_says_photo_checks_are_available():
    client, _ = make(same(NEW_TEXT))
    assert client.get("/health").json() == {"status": "ok", "photo_checks": True}


@pytest.mark.parametrize("bad", ["nope", "x" * 80, "a b c d e f g h i j k l m n o p"])
def test_unknown_or_malformed_job_is_404(bad):
    client, _ = make(same(NEW_TEXT))
    assert client.get(f"/v1/checks/{bad}").status_code == 404


def test_finished_jobs_expire():
    client, app = make(same(NEW_TEXT))
    job_id = upload(client).json()["job_id"]
    wait_done(client, job_id)
    app.state.jobs.expire_all(now=time.monotonic() + 3600)
    assert client.get(f"/v1/checks/{job_id}").status_code == 404


def test_uploads_are_rate_limited():
    client, _ = make(same(NEW_TEXT), rate_limit_per_minute=2)
    codes = [upload(client).status_code for _ in range(4)]
    assert codes[:2] == [202, 202] and codes[2:] == [429, 429]


# --- rule 7: memory only --------------------------------------------------------


def test_the_picture_is_dropped_when_the_job_ends_and_nothing_is_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for var in ("TMP", "TEMP", "TMPDIR"):
        monkeypatch.setenv(var, str(tmp_path))
    client, app = make(same(NEW_TEXT))
    data = png(300, 200)
    job_id = upload(client, data=data).json()["job_id"]
    wait_done(client, job_id)
    assert list(tmp_path.iterdir()) == [], "no file may be created for an uploaded picture"
    dump = repr(app.state.jobs.dump())
    assert str(data[:20]) not in dump and "PNG" not in dump
    assert all(j["has_image"] is False for j in app.state.jobs.dump())
    assert str(data[:20]) not in repr(app.state.store.dump())


def test_no_scores_or_progress_numbers_anywhere():
    client, _ = make(same(NEW_TEXT))
    job_id = upload(client).json()["job_id"]
    body = json.dumps(wait_done(client, job_id)).lower()
    for word in ("confidence", "score", "percent", "progress", "eta"):
        assert word not in body
