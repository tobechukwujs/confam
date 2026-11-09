"""The evaluation cases. Everything comes from the fictional Simulated Electoral Commission in
eval/record.json: honest copies (text and pictures, with and without chat wrappers), one-detail
edits of every kind (text and pictures), crops, invented notices, paraphrases and Pidgin rumours.

SYNTHETIC. These say nothing about real notices, real letterheads, stamps, or real photographs.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from eval import images as im
from eval.corpus import load_record
from eval.mutate import edits_for
from eval.wrappers import WRAPPERS

RECORD_JSON = Path(__file__).resolve().parent / "record.json"

HONEST, EDIT, CROP, INVENTED = "honest", "edit", "crop", "invented"
CONFIRMED = frozenset({"confirmed"})
NOT_VERIFIABLE = frozenset({"cannot_confirm", "not_official"})  # invented / paraphrased / rumours
ABOVE, BELOW = ("Forwarded", "~ Ngozi Eze"), ("10:42 AM",)


@dataclass(frozen=True)
class Case:
    id: str
    suite: str
    role: str  # honest | edit | crop | invented
    kind: str
    expected: frozenset[str]
    text: str
    notice_id: str | None = None
    # pictures: how to make it. None for text cases.
    degrade: str | None = None
    wrapped: bool = False
    crop: str | None = None  # "tail" | "head" for picture crops
    seed: int = 0
    note: str = ""


def render_image(case: Case) -> bytes:
    """Make the picture for an image case (deterministic)."""
    rendered = im.render(
        case.text,
        above=ABOVE if case.wrapped else (),
        below=BELOW if case.wrapped else (),
        bubble=case.wrapped and case.degrade != "lowres",
    )
    img = rendered.image
    if case.crop == "tail":
        img = im_open(im.crop_bottom(img, 0.55))
    elif case.crop == "head":
        img = im_open(im.crop_top(img, 0.34))
    return {
        "clean": im.to_png,
        "whatsapp": im.whatsapp_compress,
        "phone": lambda i: im.phone_photo(i, case.seed),
        "lowres": lambda i: im.low_resolution(i, 480),
    }[case.degrade](img)


def im_open(data: bytes):
    import io

    from PIL import Image

    return Image.open(io.BytesIO(data)).convert("RGB")


# --- honest variants (a person copies the notice, nothing changes) --------------------------

VARIANTS: dict[str, Callable[[str], str]] = {
    "identical": lambda t: t,
    "upper_case": lambda t: t.upper(),
    "lower_case": lambda t: t.lower(),
    "extra_spaces": lambda t: "  " + t.replace(" ", "   ") + "  ",
    "line_breaks": lambda t: t.replace(". ", ".\n\n"),
    "no_final_periods": lambda t: __import__("re").sub(r"\.(\s|$)", r"\1", t),
}

INVENTED_NOTICES = [
    "The Simulated Electoral Commission announces that all voters must pay N2,000 to collect their voter card. Pay at https://cards-sec.example today.",
    "Breaking: the Simulated Electoral Commission has moved polling day to Sunday 13th December. Confirm your polling unit at https://units-sec.example.",
    "The Simulated Electoral Commission announces a new voter list for Lagos Island. Download it at https://lists-sec.example before Friday.",
    "Urgent notice from the Simulated Electoral Commission: voters without a bank account cannot vote. Visit https://bank-sec.example to link your account.",
    "The Simulated Electoral Commission will pay N10,000 to every voter who registers on 30th November. Send your name to 08031234567.",
    "The Simulated Electoral Commission announces that results will be sent by text message on Saturday 12th December at 9:00 pm.",
    "Notice: the Simulated Electoral Commission has closed all registration centres from Monday 23rd November until further notice.",
    "The Simulated Electoral Commission announces extra polling days on Tuesday 15th December and Wednesday 16th December for late voters.",
    "The Simulated Electoral Commission requires every voter to bring N500 to the polling unit for a ballot paper fee.",
    "Official: the Simulated Electoral Commission has cancelled voter card collection. Cards will be posted to your home for a fee of N1,500.",
    "The Simulated Electoral Commission announces that observers no longer need accreditation. Walk in to any polling unit.",
    "Announcement: the Simulated Electoral Commission helpline is now 08099998888. Give your voter card number to the agent.",
    "The Simulated Electoral Commission has opened a new portal. Log in at https://portal-sec.example with your voter card number and password.",
    "Citizens living abroad can vote by sending a photo of their voter card to 08055550000 before 1st December.",
    "The Simulated Electoral Commission will publish provisional results on https://fastresults-sec.example at 6:00 pm on the day of the election.",
]
# A rewrite of a real notice (it shares its wording and facts): the right answer is "altered".
MODIFIED_REAL = [
    "The Simulated Electoral Commission announces that polling units will stay open until midnight on Saturday 12th December.",
    "The Simulated Electoral Commission announces that voter registration has been extended and now closes on 20th December.",
    "The Simulated Electoral Commission announces that the helpline is open from 8:00 am to 8:00 pm every day.",
]
PARAPHRASES = [  # true in spirit, but not a copy of any signed notice
    "The commission said voter registration is free.",
    "I heard that the commission will not announce results by phone.",
    "My uncle says the helpline is open on weekdays.",
    "They said you must not bring weapons to the polling unit.",
]
PIDGIN_RUMOURS = [
    "Abeg oh! Dem don move voter registration go 15th November. Make una run go register for https://register-sec.example",
    "Make una hear dis one: Simulated Electoral Commission say na N3,000 dem dey collect for voter card now.",
    "Wetin I see for group: dem say polling units go open by 6:00 am on Saturday 12th December. E correct?",
    "Dem don cancel election for my area o. Na wetin dem tell me for 08031234567.",
    "Abeg share dis one: anybody wey no get bank account no fit vote again. Na Simulated Electoral Commission talk am.",
    "Oga, Simulated Electoral Commission dey send results by text message. Dem say make you reply 1 to see am.",
    "Dem say registration don close since 10th November. Dem no go extend am again.",
    "Na so I hear say card collection don move go 20th December. Make una confirm for https://cards-sec.example",
    "Simulated Electoral Commission say make we pay N500 for observer badge. Na true?",
    "Abeg who sabi: helpline na 08077776666 now? Dem say e free.",
    "Wahala dey o! Dem say voters must carry N1,000 go polling unit for ink.",
    "I just see message say polling unit go close by 12:00 noon. Na Simulated Electoral Commission talk am?",
    "Make una no vote for Saturday o, dem don change am go Monday 14th December, na wetin dem tell me.",
    "Dem don open new website for results: https://results-sec.example. Na there una go check am.",
    "Registration no be free again o. Na N1,000 dem dey collect for Simulated Electoral Commission office.",
    "Simulated Electoral Commission announce say dem go post voter card come house. You go pay N2,000.",
    "Abeg una help me confirm: observer accreditation don close since 15th November?",
    "Dem say if you no carry voter card dem no go allow you vote, but dem no tell us say e free to collect am.",
    "Pidgin gist: dem say Saturday 12th December na public holiday for election so polling dey Sunday.",
    "Dem don announce new helpline 0800 111 2222, make una call am to register.",
]


def build(include_images: bool = True, seed: int = 20261110) -> list[Case]:
    rng = random.Random(seed)
    record, _ = load_record(RECORD_JSON)
    wrappers = list(WRAPPERS)
    cases: list[Case] = []

    # 1. honest copies, text
    for n in record:
        for vname, fn in VARIANTS.items():
            cases.append(Case(f"honest_text/{n.id}/{vname}", "honest_text", HONEST, vname, CONFIRMED, fn(n.text), n.id))
        for wname in wrappers:
            cases.append(Case(f"honest_text/{n.id}/wrap_{wname}", "honest_text", HONEST, f"wrapped:{wname}", CONFIRMED, WRAPPERS[wname](n.text), n.id))

    # 2. one-detail edits, text (bare and wrapped)
    for n in record:
        for i, e in enumerate(edits_for(n.text)):
            cases.append(Case(f"edits_text/{n.id}/{e.kind}/{i}", "edits_text", EDIT, e.kind, e.expected, e.text, n.id))
            w = wrappers[(i + len(n.id)) % len(wrappers)]
            cases.append(Case(f"edits_text_wrapped/{n.id}/{e.kind}/{i}", "edits_text_wrapped", EDIT, e.kind, e.expected, WRAPPERS[w](e.text), n.id, note=f"wrapper={w}"))

    # 3. crops, text
    for n in record:
        sentences = [s for s in __import__("re").split(r"(?<=[.!?])\s+", n.text) if s]
        half = max(1, len(sentences) // 2)
        cases.append(Case(f"crops_text/{n.id}/tail", "crops_text", CROP, "tail", frozenset({"partial"}), " ".join(sentences[:half]), n.id))
        cases.append(Case(f"crops_text/{n.id}/head", "crops_text", CROP, "head", frozenset({"partial"}), " ".join(sentences[1:]), n.id))
        cases.append(Case(f"crops_text/{n.id}/tail_wrapped_above", "crops_text", CROP, "tail+header", frozenset({"partial"}), WRAPPERS["forwarded"](" ".join(sentences[:half])), n.id))

    # 4. invented notices, paraphrases, Pidgin rumours
    for i, t in enumerate(INVENTED_NOTICES):
        cases.append(Case(f"invented/{i:02d}", "invented", INVENTED, "invented_notice", NOT_VERIFIABLE, t))
    for i, t in enumerate(MODIFIED_REAL):
        cases.append(Case(f"modified_real/{i:02d}", "modified_real", EDIT, "rewrite_of_a_real_notice", frozenset({"altered", "not_official"}), t))
    for i, t in enumerate(PARAPHRASES):
        cases.append(Case(f"paraphrase/{i:02d}", "paraphrases", INVENTED, "true_paraphrase", frozenset({"cannot_confirm"}), t))
    for i, t in enumerate(PIDGIN_RUMOURS):
        cases.append(Case(f"pidgin/{i:02d}", "pidgin_rumours", INVENTED, "pidgin_rumour", NOT_VERIFIABLE, t))

    if not include_images:
        return cases

    degrades = ["clean", "whatsapp", "phone", "lowres"]
    # 5. honest pictures
    for n in record:
        for d in degrades:
            for wrapped in (False, True):
                cases.append(Case(f"honest_image/{n.id}/{d}{'_wrapped' if wrapped else ''}", "honest_image", HONEST, d + ("+wrapper" if wrapped else ""), CONFIRMED, n.text, n.id, degrade=d, wrapped=wrapped, seed=rng.randrange(1, 50)))
    # 6. one-detail edits, pictures: up to 3 distinct kinds per notice, every degradation, wrapped
    prefer = ["date_day", "date_month", "link_host", "time", "number", "money", "phone", "weekday", "negation_removed", "word_free", "word_closes"]
    for n in record:
        by_kind: dict[str, object] = {}
        for e in edits_for(n.text):
            if e.kind in prefer and e.kind not in by_kind and "altered" in e.expected and len(e.expected) == 1:
                by_kind[e.kind] = e
        chosen = sorted(by_kind.values(), key=lambda e: prefer.index(e.kind))[:3]
        for e in chosen:
            for d in degrades:
                cases.append(Case(f"edits_image/{n.id}/{e.kind}/{d}", "edits_image", EDIT, f"{e.kind}@{d}", e.expected, e.text, n.id, degrade=d, wrapped=True, seed=rng.randrange(1, 50)))
    # 7. crops, pictures
    for n in record:
        for d in ("clean", "whatsapp"):
            cases.append(Case(f"crops_image/{n.id}/tail/{d}", "crops_image", CROP, f"tail@{d}", frozenset({"partial"}), n.text, n.id, degrade=d, crop="tail"))
    return cases


IMAGE_SUITES = {"honest_image", "edits_image", "crops_image"}
