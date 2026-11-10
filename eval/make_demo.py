"""Make the demo set: six pictures of the fictional notice that behave correctly under the real
pipeline (Tesseract, two readings, the confidence gate at its default of 95).

    uv run python eval/make_demo.py           # (re)generate fixtures/sec-sim/demo/
    uv run python eval/make_demo.py --check   # verify the committed pictures still behave

For each scenario it tries a small set of renderings and keeps the first one that gives the
intended verdict, so the set only contains pictures that really work. They are checked against the
APP's record (fixtures/sec-sim/notices.json), not the evaluation record. Fictional Simulated
Electoral Commission text only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval import images as im  # noqa: E402
from eval.corpus import NOTICES_JSON, load_record  # noqa: E402

from confam_engine import check_notice
from confam_engine.ocr import check_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, tesseract_available  # noqa: E402

OUT = ROOT / "fixtures" / "sec-sim" / "demo"
RECORD, _ = load_record(NOTICES_JSON)
CURRENT = next(n for n in RECORD if n.id == "SEC-2026-140").text
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
ABOVE, BELOW = ("Forwarded", "~ Ngozi Eze"), ("10:42 AM",)
INVENTED = "URGENT. Citizens must register at https://register-sec.example before the voter registration deadline."


def verdict_for(data: bytes):
    img = load_image(data)
    readings = [r.read(img) for r in default_readers()]
    return check_readings(readings, RECORD, record_as_of=NOW, lang="en", now=NOW)


def first_kind(v):
    return v.changes[0].kind.value if v.changes else None


# (name, file stem, text, how to degrade, accept(verdict))
SCENARIOS = [
    ("honest_confirmed", "01_honest_confirmed", CURRENT, "png",
     lambda v: v.verdict.value == "confirmed" and v.notice.id == "SEC-2026-140" and v.superseded_by is None),
    ("altered_date", "02_altered_date", CURRENT.replace("28th November", "29th November"), "png",
     lambda v: v.verdict.value == "altered" and first_kind(v) == "date" and v.changes[0].copy_ == "29th November" and v.changes[0].box is not None),
    # A changed web address on a PHOTO is never called altered at the default confidence gate of 95:
    # Tesseract gives addresses a confidence of about 84-91 at every size. So this one is a text check.
    ("altered_link", "03_altered_link_PASTE", CURRENT.replace("register.sec.example", "register-sec.example"), "text",
     lambda v: v.verdict.value == "altered" and first_kind(v) == "link" and v.changes[0].copy_ == "https://register-sec.example"),
    ("not_official", "04_not_official", INVENTED, "png",
     lambda v: v.verdict.value == "not_official" and bool(v.conflicts) and v.conflicts[0].kind.value == "link"),
    ("partial_crop", "05_partial_crop", CURRENT, "crop",
     lambda v: v.verdict.value == "partial" and v.notice.id == "SEC-2026-140"),
    ("cannot_confirm_blurry", "06_cannot_confirm_blurry", CURRENT, "blur",
     lambda v: v.verdict.value == "cannot_confirm"),
]
RENDERINGS = [(wrapped, size) for wrapped in (True, False) for size in (38, 42, 46, 50, 34)]


def render(text: str, how: str, wrapped: bool, size: int) -> bytes:
    r = im.render(text, above=ABOVE if wrapped else (), below=BELOW if wrapped else (), bubble=wrapped, font_size=size, aligned=True)
    if how == "crop":
        return im.crop_bottom(r.image, 0.55)
    if how == "blur":
        return im.blur(r.image, 7.0)
    return im.to_png(r.image)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the committed pictures, change nothing")
    args = ap.parse_args()
    if not tesseract_available():
        print("Tesseract is not installed")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    expected, failed = {}, []
    for name, stem, text, how, accept in SCENARIOS:
        if how == "text":
            path = OUT / f"{stem}.txt"
            v = check_notice(path.read_text(encoding="utf-8").strip() if args.check else text, RECORD, record_as_of=NOW, lang="en", now=NOW)
            if not accept(v):
                print(f"FAIL {stem}: {v.verdict.value}")
                failed.append(stem)
                continue
            if not args.check:
                path.write_text(text + "\n", encoding="utf-8")
                expected[stem] = {
                    "scenario": name, "mode": "paste this text into the check box (not a photo)", "verdict": v.verdict.value,
                    "notice": v.notice.id, "changes": [{"kind": c.kind.value, "copy": c.copy_, "official": c.official} for c in v.changes],
                }
            print(f"OK   {stem}: {v.verdict.value}  (text to paste)")
            continue
        path = OUT / f"{stem}.png"
        if args.check:
            v = verdict_for(path.read_bytes())
            ok = accept(v)
            print(f"{'OK  ' if ok else 'FAIL'} {stem}: {v.verdict.value}")
            if not ok:
                failed.append(stem)
            continue
        chosen = None
        for wrapped, size in RENDERINGS:
            data = render(text, how, wrapped, size)
            v = verdict_for(data)
            if accept(v):
                chosen = (data, wrapped, size, v)
                break
        if chosen is None:
            print(f"NO RENDERING WORKS for {name}")
            failed.append(stem)
            continue
        data, wrapped, size, v = chosen
        path.write_bytes(data)
        expected[stem] = {
            "scenario": name, "verdict": v.verdict.value, "reason": v.reason.value if v.reason else None,
            "notice": v.notice.id if v.notice else None,
            "changes": [{"kind": c.kind.value, "copy": c.copy_, "official": c.official} for c in v.changes],
            "conflicts": [{"kind": c.kind.value, "copy": c.copy_, "official": c.official} for c in v.conflicts],
            "rendering": {"chat_bubble": wrapped, "font_size": size}, "kb": round(len(data) / 1024, 1),
        }
        print(f"OK   {stem}: {v.verdict.value}  ({'chat bubble, ' if wrapped else ''}font {size}, {len(data) // 1024} KB)")
    if not args.check and not failed:
        (OUT / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
