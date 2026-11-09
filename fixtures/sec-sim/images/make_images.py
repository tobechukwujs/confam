"""Render fictional notice pictures for tests. Pillow only, deterministic, no OS fonts.

    uv run python fixtures/sec-sim/images/make_images.py

Only the fictional Simulated Electoral Commission (rule 9). The picture text is the notice text
itself, which already names the fictional body, so nothing here can pass for a real document.
Outputs (committed): honest.png, date_edit.png, cropped.png, blurry.png, expected.json.
expected.json gives the box (x, y, w, h, each 0-1) of the edited date in date_edit.png.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
NOTICES = json.loads((HERE.parent / "notices.json").read_text(encoding="utf-8"))["notices"]
TEXT = next(n["text"] for n in NOTICES if n["id"] == "SEC-2026-140")

W, H = 1200, 520
MARGIN = 60
FONT_SIZE = 38
LINE = 64


def font() -> ImageFont.FreeTypeFont:
    return ImageFont.load_default(size=FONT_SIZE)  # scalable built-in font, same on every OS


def layout(text: str):
    """Word-by-word layout. Returns [(word, x, y, w, h)] in pixels, wrapped inside the margins."""
    f = font()
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    x, y = MARGIN, MARGIN
    out = []
    space = probe.textlength(" ", font=f)
    for word in text.split():
        w = probe.textlength(word, font=f)
        if x + w > W - MARGIN:
            x, y = MARGIN, y + LINE
        top, bottom = probe.textbbox((0, 0), word, font=f)[1], probe.textbbox((0, 0), word, font=f)[3]
        out.append((word, x, y + top, w, bottom - top))
        x += w + space
    return out


def render(text: str, lines: int | None = None) -> tuple[Image.Image, list]:
    img = Image.new("RGB", (W, H), (252, 252, 250))
    d = ImageDraw.Draw(img)
    f = font()
    placed = layout(text)
    for word, x, y, w, h in placed:
        # draw at the layout position (textbbox top offset is already included in y)
        top = d.textbbox((0, 0), word, font=f)[1]
        d.text((x, y - top), word, font=f, fill=(20, 20, 24))
    if lines is not None:
        cut = MARGIN + lines * LINE
        img.paste((252, 252, 250), (0, cut, W, H))
    return img, placed


def box_of(placed, words: list[str]) -> list[float]:
    hit = [p for p in placed if p[0].strip(".,") in words]
    x0 = min(p[1] for p in hit) / W
    y0 = min(p[2] for p in hit) / H
    x1 = max(p[1] + p[3] for p in hit) / W
    y1 = max(p[2] + p[4] for p in hit) / H
    return [round(x0, 4), round(y0, 4), round(x1 - x0, 4), round(y1 - y0, 4)]


def main() -> None:
    honest, _ = render(TEXT)
    honest.save(HERE / "honest.png", optimize=True)

    edited_text = TEXT.replace("28th November", "29th November")
    edited, placed = render(edited_text)
    edited.save(HERE / "date_edit.png", optimize=True)

    cropped, _ = render(TEXT, lines=2)  # the lower lines are cut off
    cropped.save(HERE / "cropped.png", optimize=True)

    blurry = honest.filter(ImageFilter.GaussianBlur(radius=7)).resize((W // 3, H // 3)).resize((W, H))
    blurry.save(HERE / "blurry.png", optimize=True)

    expected = {"date_edit": {"words": ["29th", "November"], "box": box_of(placed, ["29th", "November"])}}
    (HERE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print("wrote", [p.name for p in sorted(HERE.glob("*.png"))], expected)


if __name__ == "__main__":
    main()
