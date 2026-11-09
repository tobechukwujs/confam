"""Generate the 10 probe pictures and run them through the real pipeline (Tesseract). Prints what
each one did. Nothing is tuned here: this only shows results.

    uv run python eval/probe_images.py            # writes fixtures/sec-sim/images/probe/*.jpg|png
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval import images as im  # noqa: E402
from eval.corpus import load_record  # noqa: E402

from confam_engine.ocr import check_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, tesseract_available  # noqa: E402

OUT = ROOT / "fixtures" / "sec-sim" / "images" / "probe"
RECORD, NOTICES = load_record()
CURRENT = next(n for n in RECORD if n.id == "SEC-2026-140").text
EDITED_DATE = CURRENT.replace("28th November", "29th November")
EDITED_LINK = CURRENT.replace("register.sec.example", "register-sec.example")
ABOVE = ("Forwarded", "~ Ngozi Eze")
BELOW = ("10:42 AM",)


def build():
    """name -> (bytes, extension, expected verdicts, note)"""
    out = {}
    plain = im.render(CURRENT)
    out["01_clean_honest"] = (im.to_png(plain.image), "png", {"confirmed"}, "clean screenshot, honest")
    edited = im.render(EDITED_DATE, above=ABOVE, below=BELOW, bubble=True)
    out["02_clean_wrapped_date_edit"] = (im.to_png(edited.image), "png", {"altered"}, "clean chat screenshot with Forwarded/sender/time, date changed")
    wa = im.render(CURRENT, above=ABOVE, below=BELOW, bubble=True)
    out["03_whatsapp_honest"] = (im.whatsapp_compress(wa.image), "jpg", {"confirmed"}, "chat screenshot, shrunk to 60% and JPEG quality 30, honest")
    wa_e = im.render(EDITED_DATE, above=ABOVE, below=BELOW, bubble=True)
    out["04_whatsapp_date_edit"] = (im.whatsapp_compress(wa_e.image), "jpg", {"altered"}, "same compression, date changed")
    out["05_cropped_tail"] = (im.crop_bottom(plain.image, 0.55), "png", {"partial"}, "bottom of the notice cut off")
    out["06_cropped_head"] = (im.crop_top(plain.image, 0.34), "png", {"partial"}, "first lines cut off")
    ph = im.render(CURRENT, above=ABOVE, below=BELOW, bubble=True)
    out["07_phone_photo_honest"] = (im.phone_photo(ph.image, 7), "jpg", {"confirmed"}, "photo of a screen: tilt, perspective, blur, noise, uneven light, JPEG 55")
    ph_e = im.render(EDITED_LINK, above=ABOVE, below=BELOW, bubble=True)
    out["08_phone_photo_link_edit"] = (im.phone_photo(ph_e.image, 8), "jpg", {"altered"}, "photo of a screen, web address changed")
    out["09_low_res_honest"] = (im.low_resolution(plain.image, 480), "png", {"confirmed"}, "480 px wide screenshot, honest")
    out["10_low_res_date_edit"] = (im.low_resolution(im.render(EDITED_DATE).image, 480), "png", {"altered"}, "480 px wide screenshot, date changed")
    return out


def main() -> int:
    if not tesseract_available():
        print("Tesseract is not installed")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    readers = default_readers()
    now = datetime.now(timezone.utc)
    rows = []
    for name, (data, ext, expected, note) in build().items():
        (OUT / f"{name}.{ext}").write_bytes(data)
        t0 = time.time()
        img = load_image(data)
        readings = [r.read(img) for r in readers]
        v = check_readings(readings, RECORD, record_as_of=now, lang="en", now=now)
        secs = time.time() - t0
        got = v.verdict.value + (f"/{v.reason.value}" if v.reason else "")
        changes = [(c.op.value, c.kind.value, c.official, c.copy_) for c in v.changes]
        rows.append(
            {
                "image": f"{name}.{ext}", "kb": round(len(data) / 1024, 1), "size": list(img.size),
                "note": note, "expected": sorted(expected), "got": got, "ok": v.verdict.value in expected,
                "changes": changes, "seconds": round(secs, 1),
                "reading_1": " ".join(w.text for w in readings[0].words)[:150],
                "reading_2": " ".join(w.text for w in readings[1].words)[:150],
            }
        )
    for r in rows:
        print(f"{r['image']:<34} {r['kb']:>6} KB {str(r['size']):<12} expected {'|'.join(r['expected']):<10} got {r['got']:<24} {'OK ' if r['ok'] else 'MISS'} {r['seconds']}s")
        if r["changes"]:
            print(f"    changes: {r['changes']}")
        if not r["ok"]:
            print(f"    reading 1: {r['reading_1']}")
            print(f"    reading 2: {r['reading_2']}")
    (ROOT / "eval" / "results").mkdir(exist_ok=True)
    (ROOT / "eval" / "results" / "probe_images.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
