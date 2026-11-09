"""Rule-based comparison (pipeline steps 3-8): match, compare, meaning rules, allow-list,
partial, supersession and the conflict finder.

Fictional "Simulated Electoral Commission" notices only (rule 9). No model writes any of this
(rule 3), and nothing here returns a score (rule 4).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from confam_engine import OfficialNotice, Replacement, check_notice

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
FEE_TEXT = (
    "The Simulated Electoral Commission confirms that you should not pay any fee to register. "
    "Report any request for a fee on 0800 100 2000."
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
FEE = OfficialNotice(
    id="SEC-2026-160", title="Simulated Electoral Commission: no fee for registration",
    published="2026-10-20", url="https://sec.example/notices/SEC-2026-160", text=FEE_TEXT,
)
RECORD = [OLD, NEW, FEE]


def check(text, record=RECORD):
    v = check_notice(text, record, record_as_of=AS_OF, lang="en", now=NOW)
    payload = v.model_dump(mode="json", by_alias=True)
    for ch in payload["changes"]:
        if ch.get("box") is None:
            ch.pop("box", None)
    errors = [e.message for e in VALIDATOR.iter_errors(payload)]
    assert errors == [], errors
    return v


def pairs(v):
    return {(c.op.value, c.kind.value, c.official, c.copy_) for c in v.changes}


# --- honest copies are confirmed ------------------------------------------


@pytest.mark.parametrize(
    "variant",
    [
        lambda t: t,
        lambda t: t.upper(),
        lambda t: t.lower(),
        lambda t: "  " + t.replace(" ", "   ") + "  ",
        lambda t: t.replace(". ", ".\n\n"),  # line breaks as WhatsApp wraps them
        lambda t: re.sub(r"\.(\s|$)", r"\1", t),  # sentence-final full stops dropped
        lambda t: t.replace("14th", "14"),  # an ordinal suffix is not a fact
        lambda t: t.replace("14th November", "November 14"),
        lambda t: "*" + t + "*",  # bold markers
    ],
)
def test_honest_copy_of_the_old_notice_is_confirmed_and_flagged_replaced(variant):
    v = check(variant(OLD_TEXT))
    assert v.verdict.value == "confirmed", v
    assert v.notice.id == "SEC-2026-114"
    assert v.superseded_by is not None and v.superseded_by.id == "SEC-2026-140"  # rule 2
    assert v.changes == [] and v.conflicts == []


def test_honest_copy_of_the_current_notice_is_confirmed_with_no_replacement():
    v = check(NEW_TEXT)
    assert v.verdict.value == "confirmed" and v.notice.id == "SEC-2026-140"
    assert v.superseded_by is None


# --- altered: meaning rules always count -----------------------------------


def test_a_one_digit_date_change_is_altered_not_confirmed():
    v = check(OLD_TEXT.replace("14th November", "15th November"))
    assert v.verdict.value == "altered"
    assert ("replace", "date", "14th November", "15th November") in pairs(v)
    assert v.superseded_by is None  # only a confirmed verdict may carry it
    assert v.notice.id == "SEC-2026-114"


def test_the_changed_date_of_the_current_notice():
    v = check(NEW_TEXT.replace("28th November", "29th November"))
    assert v.verdict.value == "altered" and v.notice.id == "SEC-2026-140"
    assert pairs(v) == {("replace", "date", "28th November", "29th November")}


def test_a_changed_month_is_altered():
    v = check(NEW_TEXT.replace("28th November", "28th December"))
    assert v.verdict.value == "altered"
    assert ("replace", "date", "28th November", "28th December") in pairs(v)


def test_a_swapped_link_is_altered_and_named_as_a_link():
    v = check(NEW_TEXT.replace("https://register.sec.example", "https://register-sec.example"))
    assert v.verdict.value == "altered"
    assert ("replace", "link", "https://register.sec.example", "https://register-sec.example") in pairs(v)


def test_a_dropped_negation_is_altered():
    v = check(FEE_TEXT.replace("should not pay", "should pay"))
    assert v.verdict.value == "altered" and v.notice.id == "SEC-2026-160"
    assert ("delete", "negation", "not", None) in pairs(v)


def test_a_changed_phone_number_is_altered():
    v = check(FEE_TEXT.replace("0800 100 2000", "0800 100 2001"))
    assert v.verdict.value == "altered"
    assert ("replace", "phone", "0800 100 2000", "0800 100 2001") in pairs(v)


def test_an_added_sentence_with_money_is_altered_as_an_insert():
    v = check(NEW_TEXT + " Pay a fee of N500 at the office.")
    assert v.verdict.value == "altered"
    kinds = {(c.op.value, c.kind.value) for c in v.changes}
    assert ("insert", "money") in kinds


def test_an_extra_phone_number_not_on_the_record_is_reported():
    v = check(NEW_TEXT + " Call 08012345678 now.")
    assert v.verdict.value == "altered"
    assert ("insert", "phone", None, "08012345678") in pairs(v)


def test_a_changed_word_is_reported_as_words():
    v = check(NEW_TEXT.replace("voter registration", "voter enrolment"))
    assert v.verdict.value == "altered"
    assert any(c.kind.value == "text" for c in v.changes)


def test_changes_never_carry_a_box_for_typed_text():
    v = check(NEW_TEXT.replace("28th", "29th"))
    assert all(c.box is None for c in v.changes)


# --- a single look-alike character is unclear, never confirmed or altered ---


@pytest.mark.parametrize(
    "bad",
    [
        NEW_TEXT.replace("28th", "2Bth"),  # 8 -> B
        NEW_TEXT.replace("registration", "registrat1on"),  # i -> 1 inside a word
        NEW_TEXT.replace("Commission", "Comm1ssion"),
        NEW_TEXT.replace("28th", "Z8th"),  # 2 -> Z
        NEW_TEXT.replace("closes", "c1oses"),  # l -> 1
    ],
)
def test_a_single_lookalike_character_is_cannot_confirm_unclear(bad):
    v = check(bad)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "unclear"
    assert v.notice.id == "SEC-2026-140"  # unclear needs the notice we compared with
    assert v.changes == []


def test_a_real_digit_change_is_not_mistaken_for_a_lookalike():
    v = check(NEW_TEXT.replace("28th", "29th"))
    assert v.verdict.value == "altered"


def test_a_definite_change_beats_a_lookalike_in_the_same_copy():
    v = check(NEW_TEXT.replace("28th", "29th").replace("registration", "registrat1on"))
    assert v.verdict.value == "altered"
    assert ("replace", "date", "28th November", "29th November") in pairs(v)


# --- partial: the visible part matches but the rest is cut off -------------


def test_a_cropped_tail_is_partial():
    v = check("The Simulated Electoral Commission announces that voter registration now closes on 28th November.")
    assert v.verdict.value == "partial" and v.notice.id == "SEC-2026-140"
    assert v.changes == []


def test_a_cropped_head_is_partial():
    v = check("voter registration now closes on 28th November. Register only at https://register.sec.example. Registration is free.")
    assert v.verdict.value == "partial" and v.notice.id == "SEC-2026-140"


def test_a_crop_that_also_edits_the_visible_part_is_altered():
    v = check("The Simulated Electoral Commission announces that voter registration now closes on 29th November.")
    assert v.verdict.value == "altered"
    assert ("replace", "date", "28th November", "29th November") in pairs(v)


def test_dropping_the_last_sentence_is_never_confirmed():
    v = check(NEW_TEXT.replace(" Registration is free.", ""))
    assert v.verdict.value in {"partial", "altered"}


# --- rule 1: not in the record is never fake ------------------------------


@pytest.mark.parametrize(
    "rumour",
    [
        "Collect your new ballot cards at the market square on Sunday.",
        "Polling units open at 8am on the day, bring a pen.",
        "The weather will be sunny on Monday morning.",
        "Result sheets will be published on 5th December at https://results.sec.example",
    ],
)
def test_unrelated_text_is_cannot_confirm_not_in_record_never_not_official(rumour):
    v = check(rumour)
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"
    assert v.notice is None and v.conflicts == [] and v.superseded_by is None


def test_empty_record_is_not_in_record():
    v = check("Voter registration closes on 28th November.", record=[])
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"


def test_text_with_nothing_checkable_is_no_fact():
    v = check("Please help us share this message with everyone you know")
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "no_fact"
    assert v.notice is None


def test_blank_text_is_no_fact():
    v = check("   \n ")
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "no_fact"


def test_a_tiny_fragment_never_matches_by_accident():
    v = check("Registration is free.")
    assert v.verdict.value == "cannot_confirm"


# --- conflict finder: not_official needs a contradicted official fact -------


def test_an_invented_notice_with_a_wrong_registration_link_is_not_official():
    rumour = "URGENT. Citizens must register at https://register-sec.example before the voter registration deadline."
    v = check(rumour)
    assert v.verdict.value == "not_official"
    assert v.notice.id == "SEC-2026-140"  # the current notice, not the replaced one
    (conflict,) = v.conflicts
    assert conflict.kind.value == "link"
    assert conflict.copy_ == "https://register-sec.example"
    assert conflict.official == "https://register.sec.example"
    assert conflict.quote == "Register only at https://register.sec.example."
    assert v.changes == [] and v.superseded_by is None


def test_a_wrong_link_about_something_else_is_not_called_fake():
    v = check("Download your voter card at https://cards-sec.example today for free and collect it on Sunday.")
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"


def test_a_different_date_for_a_different_event_is_not_a_conflict():
    v = check("Candidate screening holds on 3rd December at the commission office hall in your area.")
    assert v.verdict.value == "cannot_confirm" and v.reason.value == "not_in_record"


# --- every output is contract-valid and carries no score -------------------


def test_outputs_have_no_score_fields():
    for text in (OLD_TEXT, NEW_TEXT.replace("28th", "29th"), "hello", "Sunday market"):
        payload = json.dumps(check(text).model_dump(mode="json", by_alias=True)).lower()
        for word in ("confidence", "score", "percent", "grade", "probab"):
            assert word not in payload


# --- the property that matters: no edited copy is ever confirmed ------------


def mutations(text: str):
    """Many one-step edits of a notice: digit changes, swapped links, dropped or added words,
    homoglyph swaps and negations. Every one must come out as something other than confirmed."""
    out = []
    # every digit bumped
    for m in re.finditer(r"\d", text):
        d = int(m.group())
        out.append(text[: m.start()] + str((d + 1) % 10) + text[m.end():])
    # every word removed, one at a time (an ordinal suffix like "th" says nothing extra)
    for m in re.finditer(r"[A-Za-z]+", text):
        if m.group() in {"st", "nd", "rd", "th"} and text[m.start() - 1].isdigit():
            continue
        out.append(text[: m.start()] + text[m.end():])
    # every word doubled with a negation
    for m in re.finditer(r"\b(closes|pay|register|announces|confirms)\b", text):
        out.append(text[: m.end()] + " not" + text[m.end():])
    # link host changed
    out.append(re.sub(r"sec\.example", "sec-example.example", text))
    # characters swapped for look-alikes
    for src, dst in (("o", "0"), ("l", "1"), ("i", "1"), ("s", "5"), ("B", "8")):
        for m in re.finditer(src, text):
            out.append(text[: m.start()] + dst + text[m.end():])
    # an extra word, number or link appended
    # (a trailing caption such as "Not valid." is wrapper text by design: see test_wrappers.py)
    for extra in (" Call 08000000000.", " Pay N1000.", " See https://x.example."):
        out.append(text + extra)
    # reordered sentences
    parts = text.split(". ")
    if len(parts) > 2:
        out.append(". ".join(reversed(parts)))
    return [m for m in out if re.sub(r"\W+", "", m).lower() != re.sub(r"\W+", "", text).lower()]


@pytest.mark.parametrize("notice", RECORD, ids=lambda n: n.id)
def test_no_edited_copy_of_a_notice_is_ever_confirmed(notice):
    bad = []
    for edited in mutations(notice.text):
        v = check_notice(edited, RECORD, record_as_of=AS_OF, lang="en", now=NOW)
        if v.verdict.value == "confirmed":
            bad.append(edited)
    assert bad == [], f"forged copies confirmed as genuine: {bad[:3]}"


def test_the_mutations_really_exercise_many_edits():
    assert len(mutations(NEW_TEXT)) > 60


def test_a_copy_is_confirmed_only_if_it_says_exactly_what_the_notice_says():
    """Seeded fuzz: 1 to 3 random edits stacked on each notice. If the engine confirms a copy,
    that copy must tokenize to exactly the notice's own facts and words, nothing else."""
    import random

    from confam_engine.compare import tokenize

    rng = random.Random(20261109)
    confirmed_but_different = []
    for notice in RECORD:
        want = [t.cmp_key for t in tokenize(notice.text)]
        pool = mutations(notice.text)
        for _ in range(250):
            text = notice.text
            for _step in range(rng.randint(1, 3)):
                text = rng.choice(mutations(text)) if rng.random() < 0.5 else rng.choice(pool)
            v = check_notice(text, RECORD, record_as_of=AS_OF, lang="en", now=NOW)
            if v.verdict.value == "confirmed" and [t.cmp_key for t in tokenize(text)] not in (
                want,
                [t.cmp_key for t in tokenize(OLD_TEXT)],
                [t.cmp_key for t in tokenize(NEW_TEXT)],
                [t.cmp_key for t in tokenize(FEE_TEXT)],
            ):
                confirmed_but_different.append(text)
    assert confirmed_but_different == [], confirmed_but_different[:3]