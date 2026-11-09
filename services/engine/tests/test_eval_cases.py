"""The evaluation's text suites as a regression gate, and sanity checks on the cases themselves.

The picture suites are not run here (slow, need Tesseract): run `uv run python eval/run.py`.
These cases are SYNTHETIC, built from the fictional Simulated Electoral Commission."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from confam_engine import check_notice
from eval.cases import IMAGE_SUITES, RECORD_JSON, build
from eval.corpus import load_record
from eval.run import summarise

GOV = "." + "gov"  # built in pieces: the repo-wide scan for government-style addresses reads this file too
RECORD, RAW = load_record(RECORD_JSON)
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
TEXT_CASES = build(include_images=False)


def test_the_cases_are_fictional_and_safe():
    text = RECORD_JSON.read_text(encoding="utf-8")
    assert "Simulated Electoral Commission" in text or "commission" in text.lower()
    assert "INEC" not in text and GOV not in text.lower()
    for url in re.findall(r"https?://[^\s\"',)]+", text):
        host = url.split("//", 1)[1].split("/")[0].rstrip(".,")
        assert host.endswith(".example"), url
    for case in TEXT_CASES:
        assert "inec" not in case.text.lower() and GOV not in case.text.lower(), case.id


def test_case_ids_are_unique_and_every_case_has_an_expected_answer():
    ids = [c.id for c in TEXT_CASES]
    assert len(ids) == len(set(ids))
    assert all(c.expected and c.text.strip() for c in TEXT_CASES)
    assert {"honest_text", "edits_text", "edits_text_wrapped", "crops_text", "invented", "pidgin_rumours"} <= {c.suite for c in TEXT_CASES}
    assert IMAGE_SUITES.isdisjoint({c.suite for c in TEXT_CASES})


def test_every_kind_of_edit_is_in_the_suite():
    kinds = {c.kind for c in TEXT_CASES if c.suite == "edits_text"}
    for needed in ("date_day", "date_month", "time", "weekday", "number", "money", "phone", "link_host", "negation_removed", "lookalike_digit", "inserted_sentence_money", "dropped_middle_sentence", "appended_link"):
        assert needed in kinds, needed


def run_text_suites():
    rows = []
    for c in TEXT_CASES:
        v = check_notice(c.text, RECORD, record_as_of=NOW, lang="en", now=NOW)
        rows.append(
            {"role": c.role, "verdict": v.verdict.value, "got": v.verdict.value + (f"/{v.reason.value}" if v.reason else ""),
             "correct": v.verdict.value in c.expected, "notice": v.notice.id if v.notice else None,
             "superseded_by": v.superseded_by.id if v.superseded_by else None, "suite": c.suite, "id": c.id}
        )
    return rows


def test_no_forged_or_invented_copy_is_ever_confirmed_in_the_text_suites():
    rows = run_text_suites()
    bad = [r["id"] for r in rows if r["role"] in {"edit", "invented"} and r["verdict"] == "confirmed"]
    assert bad == [], bad[:5]


def test_crops_are_never_confirmed_as_complete_and_replaced_notices_are_flagged():
    rows = run_text_suites()
    assert [r["id"] for r in rows if r["role"] == "crop" and r["verdict"] == "confirmed"] == []
    assert [r["id"] for r in rows if r["role"] == "honest" and r["notice"] == "SEC-E-001" and r["verdict"] == "confirmed" and not r["superseded_by"]] == []


def test_honest_text_copies_and_every_wrapper_are_confirmed():
    """Found by the evaluation: extra spaces and line breaks used to split a time or phone number."""
    rows = [r for r in run_text_suites() if r["suite"] == "honest_text"]
    wrong = [(r["id"], r["got"]) for r in rows if r["verdict"] != "confirmed"]
    assert wrong == [], wrong[:5]


def test_summarise_counts_the_three_headline_numbers():
    rows = [
        {"role": "edit", "verdict": "confirmed", "correct": False, "got": "confirmed", "notice": None, "superseded_by": None},
        {"role": "edit", "verdict": "altered", "correct": True, "got": "altered", "notice": None, "superseded_by": None},
        {"role": "honest", "verdict": "altered", "correct": False, "got": "altered", "notice": None, "superseded_by": None},
        {"role": "honest", "verdict": "cannot_confirm", "correct": False, "got": "cannot_confirm/unclear", "notice": None, "superseded_by": None},
        {"role": "honest", "verdict": "confirmed", "correct": True, "got": "confirmed", "notice": "SEC-E-001", "superseded_by": None},
        {"role": "invented", "verdict": "confirmed", "correct": False, "got": "confirmed", "notice": None, "superseded_by": None},
    ]
    s = summarise(rows)
    assert s["forged_confirmed"] == 2
    assert s["honest_false_alarms"] == 1
    assert s["honest_not_confirmed"] == 1
    assert s["replaced_notice_not_flagged"] == 1
    assert s["correct"] == 2 and s["n"] == 6