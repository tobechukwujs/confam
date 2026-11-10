"""Photo false alarms: a genuine notice must never read as altered because of OCR noise.

(a) A token that mixes letters and digits and equals the official word after look-alike
    normalisation (4/A 0/O 1/l/I 5/S 8/B 6/G 2/Z, rn/m) is a READING SLIP, not a change. Facts
    are only standalone numbers, dates, times, money, links and phones. Typed text keeps the
    stricter rule: a look-alike there may be deliberate, so it stays cannot_confirm / unclear.
(b) A change on a low-confidence word is cannot_confirm / unclear, never altered. The threshold
    is a parameter; its default is OFF until the product owner chooses it.
(c) The change list is ordered by kind (link, money, phone, date, time, number, negation first),
    so the real edit is never buried under noise. No confidence is ever returned.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, check_notice
from confam_engine.ocr import Reading, Word, check_readings
from confam_engine.ocr.agree import DEFAULT_MIN_CONFIDENCE

SCHEMA = json.loads((Path(__file__).resolve().parents[3] / "packages/contract/verdict.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)

TEXT = (
    "The Simulated Electoral Commission announces that voter registration now closes on 28th November. "
    "Register only at https://register.sec.example. Registration is free. Report fees on 0800 100 2000."
)
NOTICE = OfficialNotice(id="SEC-2026-140", title="Simulated Electoral Commission: revised voter registration deadline",
                        published="2026-10-09", url="https://sec.example/n/140", text=TEXT)
RECORD = [NOTICE]


def reading(text: str, conf: dict[str, float] | float | None = None) -> Reading:
    words = []
    for i, w in enumerate(text.split()):
        c = conf.get(w) if isinstance(conf, dict) else conf
        words.append(Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04, c))
    return Reading(words)


def photo(a, b=None, *, min_conf=None, ca=None, cb=None):
    ra = reading(a, ca)
    rb = reading(b if b is not None else a, cb if cb is not None else ca)
    v = check_readings([ra, rb], RECORD, record_as_of=NOW, lang="en", now=NOW, min_confidence=min_conf)
    payload = v.model_dump(mode="json", by_alias=True)
    for ch in payload["changes"]:
        for key in ("box", "placement"):
            if ch.get(key) is None:
                ch.pop(key, None)
    assert [e.message for e in VALIDATOR.iter_errors(payload)] == []
    return v


def kinds(v):
    return [c.kind.value for c in v.changes]


# --- (a) reading slips ---------------------------------------------------------


# One example of every look-alike pair, each inside a real word of the notice.
SLIPS = [
    ("4nnounces", "announces"),      # 4 for A (at the start of a word, where Tesseract slips)
    ("5imulated", "Simulated"),      # 5 for S
    ("N0vember", "November"),        # 0 for O
    ("c1oses", "closes"),            # 1 for l
    ("Reg1ster", "Register"),        # 1 for i
    ("Comm1ssion", "Commission"),    # 1 for i
    ("Registrat1on", "Registration"),
    ("Z000", "2000"),                # Z for 2 inside a number
]


@pytest.mark.parametrize("bad,good", SLIPS)
def test_a_mixed_letter_digit_slip_equal_to_the_official_word_is_not_a_change(bad, good):
    text = TEXT.replace(good, bad, 1)
    assert text != TEXT
    for pair in ((text, text), (text, TEXT), (TEXT, text)):
        v = photo(*pair)
        assert v.verdict.value == "confirmed", (bad, v.verdict, v.reason, kinds(v))
        assert v.changes == []


def test_every_listed_lookalike_pair_is_a_slip_when_mixed_into_a_word():
    """4/A 0/O 1/l 1/I 5/S 8/B 6/G 2/Z and rn/m, each in a word of its own notice."""
    extra = "Bank Green Zone modern"
    notice = OfficialNotice(id="X-2", title="Simulated Electoral Commission: words", published="2026-10-09",
                            url="https://sec.example/x2", text=TEXT + " " + extra)
    pairs = [("4nnounces", "announces"), ("N0vember", "November"), ("c1oses", "closes"), ("Reg1ster", "Register"),
             ("5imulated", "Simulated"), ("8ank", "Bank"), ("6reen", "Green"), ("Z0ne", "Zone"), ("modem", "modern")]
    for bad, good in pairs:
        text = (TEXT + " " + extra).replace(good, bad, 1)
        r = reading(text)
        v = check_readings([r, r], [notice], record_as_of=NOW, now=NOW)
        assert v.verdict.value == "confirmed", (bad, good, v.verdict, kinds(v))

def test_a_slip_inside_a_date_or_phone_or_amount_that_equals_the_official_form_is_a_slip():
    for bad, good in (("2Bth November", "28th November"), ("O800 100 2000", "0800 100 2000"), ("0800 1OO 2000", "0800 100 2000")):
        v = photo(TEXT.replace(good, bad, 1))
        assert v.verdict.value == "confirmed", (bad, v.verdict, kinds(v))


def test_a_mixed_token_that_is_NOT_the_official_word_is_still_a_change():
    v = photo(TEXT.replace("announces", "4nnouncez", 1))  # z is not a look-alike of s
    assert v.verdict.value == "altered"
    assert any(c.kind.value == "text" for c in v.changes)


def test_a_real_change_to_a_fact_is_still_altered():
    for edited in (TEXT.replace("28th", "29th"), TEXT.replace("sec.example", "sec-example.example"), TEXT.replace("2000", "2001")):
        assert photo(edited).verdict.value == "altered", edited


def test_a_standalone_lookalike_is_still_unclear_not_a_slip():
    """B:00 or a lone Z are not letters-and-digits in one word: they stay uncertain."""
    base = TEXT.replace("Report fees", "Opens at 8:00 am. Report fees")
    notice = OfficialNotice(id="X-1", title="Simulated Electoral Commission: hours", published="2026-10-09", url="https://sec.example/x", text=base)
    ra = reading(base.replace("8:00", "B:00"))
    v = check_readings([ra, ra], [notice], record_as_of=NOW, now=NOW)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"


def test_typed_text_keeps_the_stricter_rule():
    """A typed look-alike may be deliberate (a homoglyph), so it is never waved through."""
    for bad in (TEXT.replace("announces", "4nnounces", 1), TEXT.replace("28th", "2Bth", 1)):
        v = check_notice(bad, RECORD, record_as_of=NOW, now=NOW)
        assert v.verdict.value != "confirmed", bad


# --- (c) the change list is ordered by kind --------------------------------------


def test_the_real_edit_is_listed_before_noise_on_a_photo():
    noisy = TEXT.replace("28th", "29th").replace("announces", "announcez").replace("Report", "Reportt")
    v = photo(noisy)
    assert v.verdict.value == "altered"
    assert kinds(v)[0] == "date", kinds(v)
    assert kinds(v).index("date") < kinds(v).index("text")


def test_changes_are_ordered_link_money_phone_date_time_number_negation_then_the_rest():
    edited = (
        "The Simulated Electoral Commission announcez that voter registration now closes on 29th November at 3:00 pm. "
        "Register only at https://register-sec.example. Registration is free. Pay N500. Report fees on 0800 100 2001."
    )
    text_v = check_notice(edited, RECORD, record_as_of=NOW, now=NOW)
    order = ["link", "money", "phone", "date", "time", "number", "negation", "weekday", "text"]
    got = kinds(text_v)
    assert got == sorted(got, key=order.index), got
    assert got[0] == "link", got
    assert got[-1] == "text" or "text" not in got


# --- (b) the confidence gate -------------------------------------------------------


def test_the_gate_is_off_by_default_until_the_owner_chooses_a_threshold():
    assert DEFAULT_MIN_CONFIDENCE is None


def test_a_change_on_a_low_confidence_word_is_unclear_never_altered():
    edited = TEXT.replace("28th", "29th")
    low = {"29th": 40.0}
    v = photo(edited, min_conf=70, ca=low)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear" and v.notice.id == "SEC-2026-140"
    assert v.changes == []


def test_the_same_change_on_a_confident_word_is_altered():
    edited = TEXT.replace("28th", "29th")
    v = photo(edited, min_conf=70, ca={"29th": 93.0})
    assert v.verdict.value == "altered" and kinds(v)[0] == "date"


def test_the_gate_applies_to_a_change_in_either_reading_and_to_ordinary_words():
    edited = TEXT.replace("voter registration", "voter enrolment")
    assert photo(edited, min_conf=70, ca={"enrolment": 95.0}, cb={"enrolment": 30.0}).verdict.value == "cannot_confirm"
    assert photo(edited, min_conf=70, ca={"enrolment": 95.0}, cb={"enrolment": 95.0}).verdict.value == "altered"


def test_with_the_gate_off_confidence_changes_nothing():
    edited = TEXT.replace("28th", "29th")
    assert photo(edited, min_conf=None, ca={"29th": 1.0}).verdict.value == "altered"


def test_unknown_confidence_is_not_treated_as_low():
    edited = TEXT.replace("28th", "29th")
    assert photo(edited, min_conf=70).verdict.value == "altered"  # typed readings carry no confidence


def test_a_genuine_notice_is_still_confirmed_whatever_the_confidence():
    v = photo(TEXT, min_conf=99, ca=50.0)
    assert v.verdict.value == "confirmed"


def test_a_missing_word_on_low_confidence_neighbours_is_unclear():
    dropped = TEXT.replace("now ", "")
    low = {"closes": 30.0, "registration": 30.0}
    assert photo(dropped, min_conf=70, ca=low).verdict.value == "cannot_confirm"


def test_no_confidence_ever_appears_in_a_verdict():
    v = photo(TEXT.replace("28th", "29th"), min_conf=70, ca={"29th": 99.0})
    text = json.dumps(v.model_dump(mode="json", by_alias=True)).lower()
    for word in ("confidence", "score", "percent", "probab"):
        assert word not in text
