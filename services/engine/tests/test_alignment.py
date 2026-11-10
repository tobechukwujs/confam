"""A copy must line up with most of a notice before it can be called an edit of it.

A short message made of common words, or one quoted sentence, shares words with a notice but is
not an edited copy of it: it must not read as "altered". It goes the not_official /
cannot_confirm way. Crops without edits are still partial. The threshold (0.45 of the notice's
words) comes from the sweep in docs/EVAL.md."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from confam_engine import OfficialNotice, check_notice
from confam_engine import evaluate as ev
from confam_engine.ocr import Reading, Word, check_readings

NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
HELPLINE = (
    "The commission helpline is 0800 200 3000 and is open from 8:00 am to 6:00 pm every weekday. "
    "Calls are free. Do not share your voter card number with anyone who calls you."
)
RESULTS = (
    "Results will be published on https://results.sec.example within 24 hours of the close of polls. "
    "The commission will not announce results by phone or text message. Any message that asks for money to see results is false."
)
REG = (
    "The Simulated Electoral Commission announces that voter registration now closes on 28th November. "
    "Register only at https://register.sec.example. Registration is free."
)
RECORD = [
    OfficialNotice(id="SEC-E-008", title="Simulated Electoral Commission: helpline", published="2026-11-03", url="https://sec.example/8", text=HELPLINE),
    OfficialNotice(id="SEC-E-006", title="Simulated Electoral Commission: publication of results", published="2026-10-28", url="https://sec.example/6", text=RESULTS),
    OfficialNotice(id="SEC-E-002", title="Simulated Electoral Commission: revised voter registration deadline", published="2026-10-09", url="https://sec.example/2", text=REG),
]


def check(text):
    return check_notice(text, RECORD, record_as_of=NOW, now=NOW)


def test_the_threshold_is_between_what_paraphrases_and_edits_line_up_with():
    # paraphrases line up with 0.22 to 0.33 of a notice, real edits with at least 0.59 (docs/EVAL.md)
    assert 0.33 < ev.MIN_ALIGNMENT_FOR_ALTERED < 0.59
    assert ev.MIN_ALIGNMENT_FOR_ALTERED == 0.45


@pytest.mark.parametrize(
    "paraphrase",
    [
        "The commission said voter registration is free.",
        "I heard that the commission will not announce results by phone.",
        "My uncle says the helpline is open on weekdays.",
        "They said you must not bring weapons to the polling unit.",
    ],
)
def test_a_paraphrase_or_a_quoted_sentence_is_not_altered(paraphrase):
    v = check(paraphrase)
    assert v.verdict.value in {"cannot_confirm", "not_official"}, v.verdict
    assert v.verdict.value != "altered" and v.verdict.value != "confirmed"
    if v.verdict.value == "cannot_confirm":
        assert v.reason.value in {"not_in_record", "no_fact"}  # never "fake" (rule 1)


def test_a_real_edit_of_the_whole_notice_is_still_altered():
    assert check(HELPLINE.replace("0800 200 3000", "0800 200 3001")).verdict.value == "altered"
    assert check(RESULTS.replace("24 hours", "25 hours")).verdict.value == "altered"


def test_a_notice_missing_a_middle_sentence_is_still_altered():
    middle = RESULTS.replace(" The commission will not announce results by phone or text message.", "")
    assert check(middle).verdict.value == "altered"


def test_a_crop_with_no_edit_is_still_partial_and_a_crop_with_an_edit_is_altered_if_it_lines_up():
    crop = "The Simulated Electoral Commission announces that voter registration now closes on 28th November."
    assert check(crop).verdict.value == "partial"
    assert check(crop.replace("28th", "29th")).verdict.value == "altered"


def test_a_short_edited_fragment_that_lines_up_with_little_of_the_notice_is_not_altered():
    fragment = "Registration is free. Register only at https://register.sec.example"
    v = check(fragment.replace("free", "paid"))
    assert v.verdict.value != "altered"


def test_the_alignment_check_can_be_switched_off_to_measure_it():
    paraphrase = "The commission said voter registration is free."
    out = ev.evaluate(paraphrase, RECORD, 0.0)
    assert out.verdict == "altered"  # what it used to say
    assert ev.evaluate(paraphrase, RECORD).verdict != "altered"


def reading(text):
    return Reading([Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04) for i, w in enumerate(text.split())])


def test_the_same_rule_applies_to_photos():
    for para in ("The commission said voter registration is free.", "I heard that the commission will not announce results by phone."):
        v = check_readings([reading(para), reading(para)], RECORD, record_as_of=NOW, now=NOW)
        assert v.verdict.value in {"cannot_confirm", "not_official"}, para
    edited = REG.replace("28th", "29th")
    assert check_readings([reading(edited), reading(edited)], RECORD, record_as_of=NOW, now=NOW).verdict.value == "altered"