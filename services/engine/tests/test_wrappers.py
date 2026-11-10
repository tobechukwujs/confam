"""A genuine notice with extra lines around it (a chat "Forwarded" label, a sender name, a
timestamp, a caption above or below) must NOT read as altered. The copy is aligned to the official
notice; text outside the aligned notice is ignored; only changes inside it count.

Still counted: anything inside the notice body, an edit at the very end or start of the notice
itself, and a link or money amount (or, after the notice, a phone number) that is not in the
record, because that is what a forger adds around a genuine notice."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, Replacement, check_notice
from confam_engine.ocr import Reading, Word, check_readings
from eval.wrappers import PAYLOAD_WRAPPERS, WRAPPERS

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] / "packages" / "contract" / "verdict.schema.json").read_text(encoding="utf-8")
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
FEE_TEXT = (
    "The Simulated Electoral Commission confirms that you should not pay any fee to register. "
    "Report any request for a fee on 0800 100 2000."
)
OLD = OfficialNotice(
    id="SEC-2026-114", title="Simulated Electoral Commission: voter registration deadline",
    published="2026-09-03", url="https://sec.example/n/114", text=OLD_TEXT,
    superseded_by=Replacement(id="SEC-2026-140", published="2026-10-09"),
)
NEW = OfficialNotice(
    id="SEC-2026-140", title="Simulated Electoral Commission: revised voter registration deadline",
    published="2026-10-09", url="https://sec.example/n/140", text=NEW_TEXT,
)
FEE = OfficialNotice(
    id="SEC-2026-160", title="Simulated Electoral Commission: no fee for registration",
    published="2026-10-20", url="https://sec.example/n/160", text=FEE_TEXT,
)
RECORD = [OLD, NEW, FEE]
NOTICES = {"old": OLD_TEXT, "new": NEW_TEXT, "fee": FEE_TEXT}


def check(text, record=RECORD):
    v = check_notice(text, record, record_as_of=AS_OF, lang="en", now=NOW)
    payload = v.model_dump(mode="json", by_alias=True)
    for ch in payload["changes"]:
        for optional in ("box", "placement"):
            if ch.get(optional) is None:
                ch.pop(optional, None)
    assert [e.message for e in VALIDATOR.iter_errors(payload)] == []
    return v


def pairs(v):
    return {(c.op.value, c.kind.value, c.official, c.copy_) for c in v.changes}


# --- a genuine notice in any wrapper is confirmed ---------------------------


@pytest.mark.parametrize("which", NOTICES)
@pytest.mark.parametrize("name", WRAPPERS)
def test_a_genuine_notice_in_any_wrapper_is_confirmed(name, which):
    v = check(WRAPPERS[name](NOTICES[which]))
    assert v.verdict.value == "confirmed", (name, which, v.verdict, v.reason, pairs(v))
    assert v.changes == [] and v.conflicts == []
    if which == "old":
        assert v.superseded_by is not None and v.superseded_by.id == "SEC-2026-140"  # rule 2 still holds


def test_wrapper_text_is_not_reported_as_a_change():
    v = check(WRAPPERS["combined"](NEW_TEXT.replace("28th November", "29th November")))
    assert v.verdict.value == "altered"
    assert pairs(v) == {("replace", "date", "28th November", "29th November")}


# --- wrapper + one real change inside the notice = altered ------------------

EDITS = {
    "date": (NEW_TEXT, lambda t: t.replace("28th November", "29th November"), ("replace", "date", "28th November", "29th November")),
    "month": (NEW_TEXT, lambda t: t.replace("28th November", "28th December"), ("replace", "date", "28th November", "28th December")),
    "link": (NEW_TEXT, lambda t: t.replace("register.sec.example", "register-sec.example"), ("replace", "link", "https://register.sec.example", "https://register-sec.example")),
    "negation": (FEE_TEXT, lambda t: t.replace("should not pay", "should pay"), ("delete", "negation", "not", None)),
    "phone": (FEE_TEXT, lambda t: t.replace("0800 100 2000", "0800 100 2001"), ("replace", "phone", "0800 100 2000", "0800 100 2001")),
}


@pytest.mark.parametrize("edit", EDITS)
@pytest.mark.parametrize("name", WRAPPERS)
def test_wrapper_plus_one_change_is_altered_with_only_that_change(name, edit):
    base, mutate, expected = EDITS[edit]
    v = check(WRAPPERS[name](mutate(base)))
    assert v.verdict.value == "altered", (name, edit, v.verdict, v.reason)
    assert pairs(v) == {expected}, (name, edit, pairs(v))


def test_a_sentence_inserted_inside_the_body_still_counts():
    body = NEW_TEXT.replace("Register only", "Pay N500 to your ward officer first. Register only")
    for name in ("forwarded", "combined", "caption_above"):
        v = check(WRAPPERS[name](body))
        assert v.verdict.value == "altered", name
        assert any(c.kind.value == "money" for c in v.changes)


def test_an_edit_at_the_very_end_of_the_notice_is_not_mistaken_for_a_caption():
    body = NEW_TEXT.replace("Registration is free.", "Registration is paid.")
    for name in ("forwarded", "caption_below", "combined", "timestamp_tail"):
        v = check(WRAPPERS[name](body))
        assert v.verdict.value == "altered", (name, v.verdict)
        assert any("paid" in (c.copy_ or "") for c in v.changes)


def test_an_edit_in_the_first_words_of_the_notice_is_not_mistaken_for_a_header():
    body = NEW_TEXT.replace("The Simulated Electoral Commission", "The Simulated Electoral Authority")
    for name in ("forwarded", "sender_name", "combined"):
        v = check(WRAPPERS[name](body))
        assert v.verdict.value == "altered", (name, v.verdict)


# --- the payload check: what a forger adds around a genuine notice ----------


@pytest.mark.parametrize("name", PAYLOAD_WRAPPERS)
def test_a_link_money_or_trailing_phone_added_around_a_notice_is_never_confirmed(name):
    v = check(PAYLOAD_WRAPPERS[name](NEW_TEXT))
    assert v.verdict.value == "altered", (name, v.verdict)
    kinds = {c.kind.value for c in v.changes}
    assert kinds & {"link", "money", "phone"}, kinds


def test_a_sender_phone_number_at_the_top_of_a_forward_is_not_a_payload():
    v = check("+234 801 234 5678\n~ Ngozi\n" + NEW_TEXT)
    assert v.verdict.value == "confirmed"


def test_a_link_the_record_already_has_is_not_a_payload():
    v = check(NEW_TEXT + "\nSee https://register.sec.example")
    assert v.verdict.value == "confirmed"


# --- crop plus wrapper, unrelated text, short fragments ---------------------


def test_a_cropped_notice_with_a_header_wrapper_is_partial():
    crop = "The Simulated Electoral Commission announces that voter registration now closes on 28th November."
    for name in ("forwarded", "sender_name", "sender_phone", "caption_above", "timestamp_head_full"):
        v = check(WRAPPERS[name](crop))
        assert v.verdict.value == "partial", (name, v.verdict)


def test_a_crop_plus_a_trailing_caption_is_never_confirmed():
    """A cut-off notice followed by a caption cannot be told from an edited ending, so it is not
    called partial. It must never be confirmed. (Listed in docs/LIMITATIONS.md.)"""
    crop = "The Simulated Electoral Commission announces that voter registration now closes on 28th November."
    for name in ("caption_below", "combined", "timestamp_tail"):
        assert check(WRAPPERS[name](crop)).verdict.value in {"altered", "partial", "cannot_confirm"}, name


def test_wrapped_unrelated_text_is_still_not_in_record():
    v = check(WRAPPERS["combined"]("Collect your new ballot cards at the market square on Sunday."))
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"


def test_a_wrapper_alone_is_nothing_to_check():
    v = check("Forwarded many times\nPlease share this with everyone, it is very important.\n10:42 AM")
    assert v.verdict.value == "cannot_confirm"
    assert v.reason.value in {"no_fact", "not_in_record"}


# --- property: wrapper + one edit inside the body is never confirmed ---------


def test_no_wrapped_edited_notice_is_ever_confirmed():
    from test_evaluate import mutations  # one-step edits of a notice body

    rng = random.Random(20261110)
    names = list(WRAPPERS)
    confirmed = []
    for notice in RECORD:
        for edited in mutations(notice.text):
            # a trailing/leading appended sentence is the wrapper position itself; those are
            # covered by the payload tests above. Here only edits that stay inside the body.
            if edited.startswith(notice.text) or edited.endswith(notice.text):
                continue
            wrapped = WRAPPERS[rng.choice(names)](edited)
            v = check_notice(wrapped, RECORD, record_as_of=AS_OF, lang="en", now=NOW)
            if v.verdict.value == "confirmed":
                confirmed.append(wrapped)
    assert confirmed == [], confirmed[:2]


# --- photos: readings that include the wrapper -------------------------------


def reading(text: str) -> Reading:
    return Reading([Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04) for i, w in enumerate(text.split())])


def photo(a: str, b: str | None = None):
    return check_readings([reading(a), reading(b if b is not None else a)], RECORD, record_as_of=AS_OF, lang="en", now=NOW)


@pytest.mark.parametrize("name", WRAPPERS)
def test_a_wrapped_genuine_photo_is_confirmed(name):
    v = photo(WRAPPERS[name](NEW_TEXT))
    assert v.verdict.value == "confirmed", (name, v.verdict, v.reason)


@pytest.mark.parametrize("name", ["forwarded", "combined", "caption_below", "status_bar_and_input"])
def test_a_wrapped_photo_with_one_changed_date_is_altered_with_a_box_on_the_date(name):
    edited = WRAPPERS[name](NEW_TEXT.replace("28th November", "29th November"))
    v = photo(edited)
    assert v.verdict.value == "altered"
    assert pairs(v) == {("replace", "date", "28th November", "29th November")}
    date = v.changes[0]
    x, y, w, h = (b.root for b in date.box)
    words = edited.split()
    i = words.index("29th")
    r = reading(edited).words
    assert x <= r[i].x + 1e-9 and x + w >= r[i + 1].x + r[i + 1].w - 1e-9


def test_a_wrapped_photo_where_only_one_reading_sees_an_edit_is_unclear():
    edited = WRAPPERS["combined"](NEW_TEXT.replace("28th November", "29th November"))
    v = photo(edited, WRAPPERS["combined"](NEW_TEXT))
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"


@pytest.mark.parametrize("name", PAYLOAD_WRAPPERS)
def test_a_payload_in_a_photo_wrapper_is_not_confirmed(name):
    assert photo(PAYLOAD_WRAPPERS[name](NEW_TEXT)).verdict.value != "confirmed"


# --- placement: what a forger adds around a genuine notice is labelled as outside it -------------


def placement_of(v, kind):
    return [(c.copy_, c.placement.value if c.placement else None) for c in v.changes if c.kind.value == kind]


def test_a_link_money_or_phone_added_after_the_notice_is_labelled_after_the_notice():
    v = check(PAYLOAD_WRAPPERS["link_below"](NEW_TEXT))
    assert placement_of(v, "link") == [("https://fast-register.example", "after_notice")]
    v = check(PAYLOAD_WRAPPERS["money_below"](NEW_TEXT))
    assert [p for _, p in placement_of(v, "money")] == ["after_notice"]
    v = check(PAYLOAD_WRAPPERS["phone_below"](NEW_TEXT))
    assert [p for _, p in placement_of(v, "phone")] == ["after_notice"]


def test_a_link_added_before_the_notice_is_labelled_before_the_notice():
    v = check(PAYLOAD_WRAPPERS["link_above"](NEW_TEXT))
    assert placement_of(v, "link") == [("https://fast-register.example", "before_notice")]


def test_a_change_inside_the_notice_has_no_placement():
    v = check(NEW_TEXT.replace("Register only", "Pay N500 to your ward officer first. Register only"))
    assert v.verdict.value == "altered"
    assert all(c.placement is None for c in v.changes)
    v = check(NEW_TEXT.replace("28th", "29th"))
    assert all(c.placement is None for c in v.changes)


def test_the_same_labels_come_from_a_photo():
    def reading(text):
        return Reading([Word(w, (i % 10) * 0.09, (i // 10) * 0.05, 0.08, 0.04) for i, w in enumerate(text.split())])

    text = PAYLOAD_WRAPPERS["link_below"](NEW_TEXT)
    v = check_readings([reading(text), reading(text)], RECORD, record_as_of=AS_OF, lang="en", now=NOW)
    assert v.verdict.value == "altered"
    assert placement_of(v, "link") == [("https://fast-register.example", "after_notice")]