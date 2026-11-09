"""Tokenizer and diff: entity kinds, normalisation, and the copy/official op convention.

Op convention (relative to the forwarded COPY, same as the contract):
  replace  both say something different
  insert   the copy has words the official text does not  (official null)
  delete   the copy leaves out words the official text has (copy null)
"""

from __future__ import annotations

import pytest

from confam_engine.compare import diff_text, tokenize
from confam_engine.compare.tokenize import MEANINGFUL


def kinds(text):
    return [(t.text, t.kind) for t in tokenize(text)]


# --- tokenizer: kinds ------------------------------------------------------


def test_a_day_and_month_is_one_date_token():
    assert kinds("closes on 14th November.") == [("closes", "text"), ("on", "text"), ("14th November", "date")]


@pytest.mark.parametrize(
    "text",
    ["14th November", "14 November", "14th of November", "November 14", "November 14, 2026", "14th November 2026", "14/11/2026", "1 Sept"],
)
def test_date_forms_are_dates(text):
    toks = tokenize(text)
    assert len(toks) == 1 and toks[0].kind == "date", toks


@pytest.mark.parametrize("text", ["8am", "8 pm", "10:30", "10:30 AM"])
def test_times(text):
    toks = tokenize(text)
    assert len(toks) == 1 and toks[0].kind == "time"


@pytest.mark.parametrize("text", ["₦500", "N500", "NGN 500", "500 naira", "N1,000.50", "₦2 million"])
def test_money(text):
    toks = tokenize(text)
    assert len(toks) == 1 and toks[0].kind == "money", toks


def test_link_excludes_trailing_punctuation():
    toks = tokenize("Register only at https://register.sec.example.")
    assert toks[-1].kind == "link" and toks[-1].text == "https://register.sec.example"


@pytest.mark.parametrize("text", ["08012345678", "+234 801 234 5678", "+2348012345678"])
def test_phone(text):
    toks = tokenize(text)
    assert len(toks) == 1 and toks[0].kind == "phone", toks


def test_weekday_number_negation_text():
    assert kinds("Monday") == [("Monday", "weekday")]
    assert kinds("2026") == [("2026", "number")]
    assert kinds("14th") == [("14th", "number")]
    assert kinds("not") == [("not", "negation")]
    assert kinds("cannot don't never") == [("cannot", "negation"), ("don't", "negation"), ("never", "negation")]
    assert kinds("registration") == [("registration", "text")]


def test_may_the_verb_is_not_a_date():
    assert kinds("you may register") == [("you", "text"), ("may", "text"), ("register", "text")]


def test_meaningful_kinds():
    assert MEANINGFUL == {"date", "time", "weekday", "number", "money", "link", "phone", "negation"}


def test_combining_tone_marks_stay_inside_words():
    # Yoruba and Igbo words with tone marks must not be split into pieces.
    words = tokenize("ọjọ́ ṣe ịbụ")
    assert [t.text for t in words] == ["ọjọ́", "ṣe", "ịbụ"]


# --- tokenizer: keys (what counts as "the same") ---------------------------


def key(text):
    (tok,) = tokenize(text)
    return tok.key


def test_equivalent_forms_share_a_key():
    assert key("14th November") == key("November 14") == key("14 november") == key("14th of November")
    assert key("N500") == key("₦500") == key("500 naira") == key("NGN 500")
    assert key("8am") == key("8:00 AM")
    assert key("08012345678") == key("+234 801 234 5678")
    assert key("https://Register.SEC.example/") == key("https://register.sec.example")
    assert key("14th") == key("14")


def test_different_facts_have_different_keys():
    assert key("14th November") != key("28th November")
    assert key("14th November") != key("14th November 2026")
    assert key("N500") != key("N5000")
    assert key("https://a.example") != key("https://b.example")
    assert key("http://a.example") != key("https://a.example")
    assert key("8am") != key("8pm")


def test_text_keys_ignore_case_and_curly_apostrophes():
    assert key("Registration") == key("registration")
    assert tokenize("don’t")[0].key == tokenize("don't")[0].key


# --- diff ------------------------------------------------------------------

OLD = "The Commission announces that voter registration closes on 14th November. Register only at https://register.sec.example. Registration is free."
NEW = "The Commission announces that voter registration now closes on 28th November. Register only at https://register.sec.example. Registration is free."


def changes(copy_text, official_text):
    return [(d.op, d.kind, d.official, d.copy) for d in diff_text(copy_text, official_text)]


def test_identical_text_has_no_changes():
    assert diff_text(OLD, OLD) == []


def test_case_and_punctuation_do_not_count():
    assert diff_text("Registration is free.", "registration is free") == []


def test_replaced_date_and_added_word():
    got = changes(OLD, NEW)
    assert ("replace", "date", "28th November", "14th November") in got
    assert ("delete", "text", "now", None) in got  # the old copy leaves out "now"
    assert len(got) == 2


def test_equivalent_date_forms_are_not_a_change():
    assert diff_text("closes 14th November", "closes November 14") == []


def test_added_words_in_the_copy_are_an_insert():
    got = changes("Registration is free. Fee: 500 naira", "Registration is free.")
    assert ("insert", "money", None, "500 naira") in got
    assert ("insert", "text", None, "Fee") in got


def test_a_dropped_negation_is_a_delete_of_kind_negation():
    got = changes("You should register", "You should not register")
    assert got == [("delete", "negation", "not", None)]


def test_a_link_swap_is_a_replace_of_kind_link():
    got = changes("Register at https://b.example today", "Register at https://a.example today")
    assert got == [("replace", "link", "https://a.example", "https://b.example")]


def test_a_changed_word_run_is_one_text_replace():
    got = changes("closes at the old office", "closes at the new regional office")
    assert got == [("replace", "text", "new regional", "old")]


def test_mismatched_kinds_still_pair_as_a_replace():
    got = changes("closes on 14th", "closes on 28th November")
    assert got == [("replace", "date", "28th November", "14th")]


def test_spans_point_into_the_copy_tokens():
    d = diff_text(OLD, NEW)
    date = next(x for x in d if x.kind == "date")
    toks = tokenize(OLD)
    assert toks[date.old_span[0]].text == "14th November"


def test_to_change_has_exactly_the_contract_keys_and_no_box():
    d = diff_text(OLD, NEW)[0].to_change()
    assert set(d) == {"op", "kind", "official", "copy"}
