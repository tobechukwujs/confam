"""Render fictional notice pictures in the ways real ones arrive: a clean screenshot, a chat
screenshot that was compressed on the way, a cropped one, a phone photo of a screen, a
low-resolution one. Pillow only, deterministic (fixed seeds), no OS fonts. Fictional
Simulated Electoral Commission text only (rule 9): nothing here can pass for a real document.
"""

from __future__ import annotations

import io
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

BG = (252, 252, 250)
INK = (20, 20, 24)
GREY = (110, 110, 118)


@dataclass
class Rendered:
    image: Image.Image
    body_words: list[tuple[str, float, float, float, float]]  # word + normalised box (x, y, w, h)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.load_default(size=size)  # scalable built-in font: same on every OS


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: float):
    """[(word, x, line_index)] with greedy wrapping inside max_width."""
    out, x, line = [], 0.0, 0
    space = draw.textlength(" ", font=font)
    for word in text.split():
        w = draw.textlength(word, font=font)
        if x + w > max_width and x > 0:
            x, line = 0.0, line + 1
        out.append((word, x, line, w))
        x += w + space
    return out, line + 1


def render(
    text: str,
    *,
    above: tuple[str, ...] = (),
    below: tuple[str, ...] = (),
    width: int = 1200,
    font_size: int = 38,
    bubble: bool = False,
    aligned: bool = False,
) -> Rendered:
    """A notice (plus optional chat-style lines above and below) as a picture.

    `aligned=True` puts every word on one shared baseline. The default places each word by its own
    glyph top, which makes short words (announces, now, on) ride a little high: the evaluation
    uses that, so its numbers stay comparable; the demo set uses `aligned=True` so it looks right."""
    pad = 60
    body_font, small = _font(font_size), _font(int(font_size * 0.72))
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    inner = width - 2 * pad - (40 if bubble else 0)
    words, body_lines = _wrap(probe, text, body_font, inner)
    line_h, small_h = int(font_size * 1.7), int(font_size * 1.2)
    height = pad * 2 + len(above) * small_h + body_lines * line_h + len(below) * small_h + (20 if bubble else 0)

    img = Image.new("RGB", (width, height), (236, 236, 236) if bubble else BG)
    d = ImageDraw.Draw(img)
    x0 = pad + (20 if bubble else 0)
    if bubble:
        d.rounded_rectangle((pad // 2, pad // 2, width - pad // 2, height - pad // 2), radius=28, fill=(255, 255, 255))
    y = pad
    for line in above:
        d.text((x0, y), line, font=small, fill=GREY)
        y += small_h
    placed = []
    reference_top = d.textbbox((0, 0), "Hg", font=body_font)[1]
    for word, wx, li, w in words:
        top = reference_top if aligned else d.textbbox((0, 0), word, font=body_font)[1]
        px, py = x0 + wx, y + li * line_h
        d.text((px, py - top + 6), word, font=body_font, fill=INK)
        bb = d.textbbox((px, py - top + 6), word, font=body_font)
        placed.append((word, bb[0] / width, bb[1] / height, (bb[2] - bb[0]) / width, (bb[3] - bb[1]) / height))
    y += body_lines * line_h
    for line in below:
        d.text((x0, y), line, font=small, fill=GREY)
        y += small_h
    return Rendered(img, placed)


def box_of(rendered: Rendered, words: list[str]) -> list[float]:
    hit = [p for p in rendered.body_words if p[0].strip(".,") in words]
    x0 = min(p[1] for p in hit)
    y0 = min(p[2] for p in hit)
    x1 = max(p[1] + p[3] for p in hit)
    y1 = max(p[2] + p[4] for p in hit)
    return [round(x0, 4), round(y0, 4), round(x1 - x0, 4), round(y1 - y0, 4)]


# --- the ways a picture degrades on its way to us -------------------------------


def to_png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def to_jpeg(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    return buf.getvalue()


def whatsapp_compress(img: Image.Image) -> bytes:
    """A chat app shrinks the picture and re-encodes it as a fairly strong JPEG."""
    small = img.resize((int(img.width * 0.6), int(img.height * 0.6)), Image.LANCZOS)
    return to_jpeg(small, 30)


def low_resolution(img: Image.Image, width: int = 480) -> bytes:
    small = img.resize((width, max(1, round(img.height * width / img.width))), Image.LANCZOS)
    return to_png(small)


def blur(img: Image.Image, radius: float = 7.0) -> bytes:
    """Out of focus: a heavy blur, then shrunk and enlarged so the detail is really gone."""
    soft = img.filter(ImageFilter.GaussianBlur(radius))
    small = soft.resize((max(1, img.width // 3), max(1, img.height // 3)), Image.LANCZOS)
    return to_png(small.resize(img.size, Image.BICUBIC))


def crop_bottom(img: Image.Image, keep_fraction: float) -> bytes:
    return to_png(img.crop((0, 0, img.width, int(img.height * keep_fraction))))


def crop_top(img: Image.Image, drop_fraction: float) -> bytes:
    return to_png(img.crop((0, int(img.height * drop_fraction), img.width, img.height)))


def phone_photo(img: Image.Image, seed: int = 7) -> bytes:
    """A photograph of a screen: a little tilt and perspective, soft focus, sensor noise,
    uneven light, a faint pixel grid, and phone JPEG compression."""
    rng = random.Random(seed)
    w, h = img.size
    canvas = Image.new("RGB", (int(w * 1.12), int(h * 1.35)), (58, 52, 48))  # the table around the screen
    canvas.paste(img, (int(w * 0.06), int(h * 0.17)))
    canvas = canvas.rotate(2.2 + 0.2 * (seed % 5), resample=Image.BICUBIC, fillcolor=(58, 52, 48))
    cw, ch = canvas.size
    shrink = 0.045
    coeffs = _perspective(
        [(0, 0), (cw, 0), (cw, ch), (0, ch)],
        [(cw * shrink, ch * 0.012), (cw * (1 - shrink * 0.4), 0), (cw, ch * 0.99), (0, ch)],
    )
    canvas = canvas.transform((cw, ch), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(58, 52, 48))
    canvas = canvas.filter(ImageFilter.GaussianBlur(1.1))
    # screen pixel grid (moire-ish) and uneven lighting
    grid = Image.new("L", canvas.size, 0)
    gd = ImageDraw.Draw(grid)
    for x in range(0, cw, 3):
        gd.line([(x, 0), (x, ch)], fill=14)
    canvas = ImageChops_subtract(canvas, grid)
    light = ImageOps.autocontrast(Image.linear_gradient("L").resize(canvas.size).rotate(25, fillcolor=128))
    canvas = Image.composite(canvas, ImageOps.autocontrast(canvas, cutoff=0), Image.new("L", canvas.size, 255))
    canvas = Image.blend(canvas, Image.merge("RGB", (light, light, light)), 0.10)
    # sensor noise from the seed, so the same seed always gives the same picture
    noise = Image.frombytes("L", canvas.size, rng.randbytes(canvas.size[0] * canvas.size[1])).convert("RGB")
    canvas = Image.blend(canvas, noise, 0.07)
    canvas = canvas.resize((1000, round(ch * 1000 / cw)), Image.LANCZOS)
    return to_jpeg(canvas, 55)


def ImageChops_subtract(img: Image.Image, mask: Image.Image) -> Image.Image:
    from PIL import ImageChops

    return ImageChops.subtract(img, Image.merge("RGB", (mask, mask, mask)))


def _perspective(src, dst):
    """Coefficients for Image.transform(PERSPECTIVE): maps output points (dst) back to input (src)."""
    import itertools

    rows, rhs = [], []
    for (x, y), (u, v) in zip(dst, src):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rhs.append(u)
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        rhs.append(v)
    n = 8
    a = [r[:] + [b] for r, b in zip(rows, rhs)]
    for col, _ in itertools.product(range(n), [0]):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    return [a[i][n] / a[i][i] for i in range(n)]
