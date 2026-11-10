"""Image checks: two readings must agree. These tests use hand-built readings, so they need no
OCR binary. A change counts only if BOTH readings show it at the same spot. A disagreement on a
fact (digit, date, money, link, phone, negation) is cannot_confirm, never confirmed and never altered."""

from __future__ import annotations

import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, Replacement
from confam_engine.ocr import Reading, Word, check_readings

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] / "packages" / "contract" / "verdict.schema.json").read_text(
        encoding="utf-8"
    )
)
VALIDATOR = Draft202012Validator(SCHEMA)
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
AS_OF = datetime(2026, 11, 8, 11, 30, tzinfo=timezone.utc)

OLD_TEXT = (
    "The Simulated Electoral Commission announces that voter registration closes on 14th November. "
    "Register only at https://register.sec.example. Registration is free."
)
NEW_TEXT = (
    "The Simulated Electoral Commission announces that voter registration now closes on 28th November. "
    "Register only at https://register.sec.example. Registration is free."
)
OLD = OfficialNotice(
    id="SEC-2026-114", title="Simulated Electoral Commission: voter registration deadline",
    published="2026-09-03", url="https://sec.example/notices/SEC-2026-114", text=OLD_TEXT,
    superseded_by=Replacement(id="SEC-2026-140", published="2026-10-09"),
)
NEW = OfficialNotice(
    id="SEC-2026-140", title="Simulated Electoral Commission: revised voter registration deadline",
    published="2026-10-09", url="https://sec.example/notices/SEC-2026-140", text=NEW_TEXT,
)
RECORD = [OLD, NEW]


def reading(text: str) -> Reading:
    """Lay the words of `text` out on a grid, ten to a row, as normalised boxes."""
    words = []
    for i, w in enumerate(text.split()):
        words.append(Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04))
    return Reading(words)


def check(a: str, b: str, record=RECORD):
    v = check_readings([reading(a), reading(b)], record, record_as_of=AS_OF, lang="en", now=NOW)
    payload = v.model_dump(mode="json", by_alias=True)
    for ch in payload["changes"]:
        for optional in ("box", "placement"):
            if ch.get(optional) is None:
                ch.pop(optional, None)
    errors = [e.message for e in VALIDATOR.iter_errors(payload)]
    assert errors == [], errors
    return v


def pairs(v):
    return {(c.op.value, c.kind.value, c.official, c.copy_) for c in v.changes}


def test_two_matching_readings_of_the_current_notice_are_confirmed():
    v = check(NEW_TEXT, NEW_TEXT)
    assert v.verdict.value == "confirmed" and v.notice.id == "SEC-2026-140" and v.superseded_by is None


def test_two_matching_readings_of_the_old_notice_are_confirmed_and_flagged_replaced():
    v = check(OLD_TEXT, OLD_TEXT)
    assert v.verdict.value == "confirmed" and v.superseded_by.id == "SEC-2026-140"


def test_a_change_both_readings_show_is_altered_with_a_box():
    edited = NEW_TEXT.replace("28th November", "29th November")
    v = check(edited, edited)
    assert v.verdict.value == "altered"
    assert ("replace", "date", "28th November", "29th November") in pairs(v)
    change = next(c for c in v.changes if c.kind.value == "date")
    assert change.box is not None
    x, y, w, h = (b.root for b in change.box)
    assert 0 <= x <= 1 and 0 <= y <= 1 and w > 0 and h > 0 and x + w <= 1.0001 and y + h <= 1.0001
    # the box lies over the words "29th November" of the copy
    words = edited.split()
    i = words.index("29th")
    first = reading(edited).words[i]
    last = reading(edited).words[i + 1]
    assert x <= first.x + 1e-9 and x + w >= last.x + last.w - 1e-9


def test_a_change_only_one_reading_shows_is_never_altered_or_confirmed():
    edited = NEW_TEXT.replace("28th November", "29th November")
    for a, b in ((edited, NEW_TEXT), (NEW_TEXT, edited)):
        v = check(a, b)
        assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear", v.verdict
        assert v.notice.id == "SEC-2026-140"


def test_a_look_alike_mixed_into_a_word_in_a_photo_is_a_reading_slip_not_unclear():
    """Changed rule (photo false alarms): 2Bth equals 28th after look-alike normalisation and mixes
    a letter and a digit in one word, so it is OCR noise. Typed text keeps the stricter rule."""
    for a, b in ((NEW_TEXT.replace("28th", "2Bth"), NEW_TEXT), (NEW_TEXT, NEW_TEXT.replace("28th", "2Bth")), (NEW_TEXT.replace("28th", "2Bth"),) * 2):
        assert check(a, b).verdict.value == "confirmed"


def test_readings_that_disagree_on_a_standalone_fact_are_unclear():
    v = check(NEW_TEXT.replace("28th", "29th"), NEW_TEXT)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"


def test_both_readings_showing_a_standalone_lookalike_are_unclear_not_altered():
    notice = OfficialNotice(
        id="SEC-2026-150", title="Simulated Electoral Commission: hours", published="2026-10-09",
        url="https://sec.example/n/150",
        text="The Simulated Electoral Commission announces that polling units open at 8:00 am on Saturday and close at 2:00 pm. Bring your voter card.",
    )
    bad = notice.text.replace("8:00", "B:00")
    v = check(bad, bad, record=[notice])
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"

def test_readings_that_disagree_on_what_the_change_is_are_unclear():
    a = NEW_TEXT.replace("28th", "29th")
    b = NEW_TEXT.replace("28th", "27th")
    v = check(a, b)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"


def test_a_slip_in_an_ordinary_word_in_one_reading_is_noise():
    v = check(NEW_TEXT.replace("Commission", "Commisslon"), NEW_TEXT)
    assert v.verdict.value == "confirmed"


def test_a_changed_word_both_readings_show_is_altered_as_words():
    edited = NEW_TEXT.replace("voter registration", "voter enrolment")
    v = check(edited, edited)
    assert v.verdict.value == "altered" and any(c.kind.value == "text" for c in v.changes)


def test_a_dropped_negation_in_one_reading_only_is_unclear():
    fee = OfficialNotice(
        id="SEC-2026-160", title="Simulated Electoral Commission: no fee for registration",
        published="2026-10-20", url="https://sec.example/n/160",
        text="The Simulated Electoral Commission confirms that you should not pay any fee to register.",
    )
    good = fee.text
    bad = fee.text.replace("should not pay", "should pay")
    v = check(bad, good, record=[fee])
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"
    v2 = check(bad, bad, record=[fee])
    assert v2.verdict.value == "altered"


def test_a_crop_both_readings_show_is_partial():
    crop = "The Simulated Electoral Commission announces that voter registration now closes on 28th November."
    v = check(crop, crop)
    assert v.verdict.value == "partial" and v.notice.id == "SEC-2026-140" and v.changes == []


def test_unrelated_text_is_not_in_record():
    v = check("Collect your new ballot cards at the market square on Sunday.", "Collect your new ballot cards at the market square on Sunday.")
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"


def test_a_photo_with_no_usable_text_is_unclear_with_no_notice():
    """Approved: unclear may carry notice null ONLY when OCR read no usable text."""
    for a, b in (("", ""), ("x", "~ ."), ("ok", "")):
        v = check(a, b)
        assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear", (a, b)
        assert v.notice is None and v.changes == [] and v.conflicts == []


def test_unclear_with_a_null_notice_never_happens_when_text_was_read():
    """Readable text that matches nothing is not_in_record, and an unclear verdict about a
    readable photo always names the notice it compared with."""
    v = check("Collect your new ballot cards at the market square on Sunday.", "Collect your new ballot cards at the market square on Sunday.")
    assert v.reason.value == "not_in_record"
    v = check(NEW_TEXT.replace("28th", "29th"), NEW_TEXT)
    assert v.reason.value == "unclear" and v.notice is not None

def test_one_reading_that_cannot_find_the_notice_does_not_confirm():
    # reading B is garbage: only reading A matches, so nothing can be confirmed or altered
    v = check(NEW_TEXT, "zzz qqq xxx www vvv uuu ttt sss")
    assert v.verdict.value != "confirmed"


def test_a_single_reading_is_not_enough_for_an_image():
    with pytest.raises(ValueError):
        check_readings([reading(NEW_TEXT)], RECORD, record_as_of=AS_OF)


def test_boxes_are_clamped_to_the_image():
    edited = NEW_TEXT.replace("28th November", "29th November")
    v = check(edited, edited)
    for c in v.changes:
        if c.box:
            vals = [b.root for b in c.box]
            assert all(0 <= x <= 1 for x in vals)


def test_no_edit_in_either_reading_is_ever_confirmed():
    """Seeded: stack one to three edits across the two readings; confirmed only when both readings carry exactly the notice's facts."""
    from confam_engine.compare import tokenize

    # Facts (dates, numbers, money, links, phones, weekdays, negations) must match exactly.
    # A slip in an ordinary word seen by only one reading is OCR noise by design.
    def facts(text: str) -> list[str]:
        return [t.cmp_key for t in tokenize(text) if t.meaningful]

    rng = random.Random(20261109)
    want = facts(NEW_TEXT)

    def edit(text: str) -> str:
        # (a look-alike mixed into a word is now a reading slip on a photo, so it is not an edit here)
        kind = rng.choice(["digit", "drop", "negate", "link", "append"])
        if kind == "digit":
            ms = list(re.finditer(r"\d", text))
            m = rng.choice(ms)
            return text[: m.start()] + str((int(m.group()) + 1) % 10) + text[m.end():]
        if kind == "drop":
            ms = list(re.finditer(r"[A-Za-z]{3,}", text))
            m = rng.choice(ms)
            return text[: m.start()] + text[m.end():]
        if kind == "negate":
            return text.replace("closes", "closes not", 1)
        if kind == "link":
            return text.replace("sec.example", "sec-example.example")
        if kind == "lookalike":
            return re.sub("o", "0", text, count=1)
        return text + " Pay N500."

    wrong = []
    for _ in range(300):
        a, b = NEW_TEXT, NEW_TEXT
        for _step in range(rng.randint(1, 3)):
            if rng.random() < 0.5:
                a = edit(a)
            if rng.random() < 0.5:
                b = edit(b)
            if rng.random() < 0.3:
                a = b = edit(a)
        v = check(a, b)
        if v.verdict.value == "confirmed" and not (facts(a) == want and facts(b) == want):
            wrong.append((a, b))
    assert wrong == [], wrong[:2]
