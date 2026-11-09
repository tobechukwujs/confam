"""API tests: POST /v1/checks (text), GET /v1/verdicts/{code}, rules 1, 2, 4 and 7."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from confam_api.app import create_app
from confam_api.record import Record, load_record
from confam_api.settings import Settings
from confam_engine import OfficialNotice, RecordError, Replacement, supersession_for

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "packages/contract/verdict.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
SAMPLES = json.loads((ROOT / "fixtures/sec-sim/sample-verdicts.json").read_text(encoding="utf-8"))
SAMPLES = {k: v for k, v in SAMPLES.items() if not k.startswith("_")}

RECORD = load_record(ROOT / "fixtures/sec-sim/notices.json")
OLD = next(n for n in RECORD.notices if n.id == "SEC-2026-114")
CURRENT = next(n for n in RECORD.notices if n.id == "SEC-2026-140")


def make_client(**overrides) -> tuple[TestClient, object]:
    settings = Settings(seed_samples=False, cors_origins=("https://app.example",), **overrides)
    app = create_app(settings=settings, record=RECORD, readers=None)
    return TestClient(app), app


def post(client, text, **extra):
    return client.post("/v1/checks", json={"text": text, **extra})


def assert_valid(payload):
    errors = list(VALIDATOR.iter_errors(payload))
    assert errors == [], [e.message for e in errors]


# --- fixtures are valid ----------------------------------------------------


@pytest.mark.parametrize("name", sorted(SAMPLES))
def test_every_sample_verdict_is_schema_valid(name):
    assert_valid(SAMPLES[name])


def test_samples_cover_all_five_verdicts_and_replaced():
    kinds = {s["verdict"] for s in SAMPLES.values()}
    assert kinds == {"confirmed", "altered", "not_official", "partial", "cannot_confirm"}
    assert any(s["superseded_by"] for s in SAMPLES.values())


def test_sample_notices_are_all_from_the_fictional_commission():
    for sample in SAMPLES.values():
        if sample["notice"]:
            assert sample["notice"]["id"].startswith("SEC-")
            assert "Simulated Electoral Commission" in sample["notice"]["title"]
            assert "inec" not in json.dumps(sample).lower()


# --- rule 1 ----------------------------------------------------------------


def test_text_not_in_record_is_cannot_confirm_not_in_record():
    client, _ = make_client()
    res = post(client, "Collect your new ballot cards at the market square on Sunday.")
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"] == "cannot_confirm"
    assert body["reason"] == "not_in_record"
    assert body["verdict"] != "not_official"
    assert_valid(body)


# --- rule 2 ----------------------------------------------------------------


def test_text_matching_a_replaced_notice_sets_superseded_by():
    client, _ = make_client()
    body = post(client, OLD.text).json()
    assert body["verdict"] == "confirmed"
    assert body["superseded_by"]["id"] == "SEC-2026-140"
    assert_valid(body)


def test_text_matching_current_notice_has_no_superseded_by():
    client, _ = make_client()
    body = post(client, CURRENT.text).json()
    assert body["verdict"] == "confirmed" and body["superseded_by"] is None


def test_replaced_check_carries_url_title_and_changes_from_the_record():
    client, _ = make_client()
    sup = post(client, OLD.text).json()["superseded_by"]
    assert sup["url"] == CURRENT.url and sup["title"] == CURRENT.title
    got = {(c["op"], c["kind"], c["official"], c["copy"]) for c in sup["changes"]}
    assert ("replace", "date", "28th November", "14th November") in got
    assert all("box" not in c for c in sup["changes"])


def test_cache_hit_still_flags_supersession():
    """A cached confirmed verdict must be re-checked for supersession on a hit."""
    client, app = make_client()
    first = post(client, CURRENT.text).json()
    assert first["superseded_by"] is None
    # The record changes: SEC-2026-140 is now replaced by a newer notice.
    newest = OfficialNotice(
        id="SEC-2026-199",
        title="Simulated Electoral Commission: voter registration extended",
        published="2026-11-07",
        url="https://sec.example/notices/SEC-2026-199",
        text=CURRENT.text.replace("28th November", "5th December"),
    )
    newer = replace(CURRENT, superseded_by=Replacement(id="SEC-2026-199", published="2026-11-07"))
    app.state.holder.record = Record(
        notices=[OLD, newer, newest], record_as_of=RECORD.record_as_of
    )
    second = post(client, CURRENT.text).json()
    assert second["code"] == first["code"], "second call should be a cache hit"
    assert second["superseded_by"]["id"] == "SEC-2026-199"
    got = {(c["op"], c["kind"], c["official"], c["copy"]) for c in second["superseded_by"]["changes"]}
    assert ("replace", "date", "5th December", "28th November") in got
    assert_valid(second)
    # and the public page serves the updated flag too
    assert client.get(f"/v1/verdicts/{first['code']}").json()["superseded_by"]["id"] == "SEC-2026-199"


def test_sample_replaced_verdict_matches_what_the_engine_computes():
    """Samples are static JSON; this stops them drifting from the record."""
    for name, sample in SAMPLES.items():
        if not sample["superseded_by"]:
            continue
        notice = RECORD.get(sample["notice"]["id"])
        assert notice is not None, name
        assert sample["superseded_by"] == supersession_for(notice, RECORD.notices), name


def test_loading_a_record_with_a_dangling_replacement_fails(tmp_path):
    path = tmp_path / "notices.json"
    path.write_text(
        json.dumps(
            {
                "record_as_of": "2026-11-08T09:00:00+01:00",
                "notices": [
                    {
                        "id": "SEC-2026-114", "title": "t", "published": "2026-09-03",
                        "url": "https://sec.example/n", "text": "x",
                        "superseded_by": {"id": "SEC-NOPE", "published": "2026-10-09"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RecordError):
        load_record(path)


# --- public verdict page data ----------------------------------------------


def test_verdict_can_be_fetched_by_code_and_hyphenated_code():
    client, _ = make_client()
    body = post(client, CURRENT.text).json()
    code = body["code"]
    assert client.get(f"/v1/verdicts/{code}").json() == body
    hyphenated = f"{code[:4]}-{code[4:]}"
    assert client.get(f"/v1/verdicts/{hyphenated}").json()["code"] == code
    assert client.get(f"/v1/verdicts/{code.lower()}").status_code == 200


def test_unknown_code_is_404():
    client, _ = make_client()
    assert client.get("/v1/verdicts/ZZZZZZZZ").status_code == 404
    assert client.get("/v1/verdicts/not-a-code").status_code == 404


def test_expired_check_is_404():
    client, app = make_client()
    code = post(client, CURRENT.text).json()["code"]
    app.state.store.expire_all(now=datetime.now(timezone.utc) + timedelta(days=31))
    assert client.get(f"/v1/verdicts/{code}").status_code == 404


# --- rule 7: nothing personal kept ----------------------------------------


def test_pasted_text_is_not_kept_anywhere_in_the_store():
    client, app = make_client()
    secret = "my private forward from +2348012345678 about SEC"
    post(client, secret)
    assert secret not in repr(app.state.store.dump())
    assert "2348012345678" not in repr(app.state.store.dump())


# --- samples ---------------------------------------------------------------


def test_samples_are_served_only_when_seeding_is_on():
    off, _ = make_client()
    assert off.get("/v1/verdicts/R3P7ACED").status_code == 404
    on = TestClient(create_app(settings=Settings(seed_samples=True), record=RECORD))
    body = on.get("/v1/verdicts/R3P7ACED").json()
    assert body["superseded_by"]["id"] == "SEC-2026-140"


def test_samples_do_not_expire():
    on_app = create_app(settings=Settings(seed_samples=True), record=RECORD)
    on_app.state.store.expire_all(now=datetime.now(timezone.utc) + timedelta(days=400))
    assert TestClient(on_app).get("/v1/verdicts/R3P7ACED").status_code == 200


# --- input handling --------------------------------------------------------


@pytest.mark.parametrize("text", ["", "   ", "x" * 5001])
def test_bad_text_is_422(text):
    client, _ = make_client()
    assert post(client, text).status_code == 422


def test_unknown_language_is_422():
    client, _ = make_client()
    assert post(client, "hello", lang="fr").status_code == 422


def test_language_is_echoed():
    client, _ = make_client()
    assert post(client, "hello there", lang="pcm").json()["lang"] == "pcm"


def test_image_checks_are_not_available_yet():
    client, _ = make_client()
    res = client.post("/v1/checks", json={"image_url": "https://x.example/a.png"})
    assert res.status_code == 422


# --- CORS and rate limit ---------------------------------------------------


def test_cors_allows_configured_origin_only():
    client, _ = make_client()
    ok = client.options(
        "/v1/checks",
        headers={"Origin": "https://app.example", "Access-Control-Request-Method": "POST"},
    )
    assert ok.headers.get("access-control-allow-origin") == "https://app.example"
    bad = client.options(
        "/v1/checks",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in bad.headers


def test_rate_limit_returns_429_with_plain_message():
    client, _ = make_client(rate_limit_per_minute=3)
    codes = [post(client, f"hello {i}").status_code for i in range(5)]
    assert codes[:3] == [200, 200, 200]
    assert codes[3:] == [429, 429]
    assert "try again" in post(client, "hello").json()["detail"].lower()


def test_no_score_field_in_any_response():
    client, _ = make_client()
    text = json.dumps(post(client, CURRENT.text).json()).lower()
    for word in ("confidence", "score", "percent", "grade", "probability"):
        assert word not in text


def test_health():
    client, _ = make_client()
    assert client.get("/health").json() == {"status": "ok", "photo_checks": False}
