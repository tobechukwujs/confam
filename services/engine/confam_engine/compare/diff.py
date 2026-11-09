"""Token diff between the forwarded COPY and the OFFICIAL text.

Ops are relative to the copy, matching the contract:
  replace  the copy and the official text say different things
  insert   the copy has words the official text does not (official is null)
  delete   the copy leaves out words the official text has (copy is null)

Meaning-bearing tokens (dates, numbers, money, links, phones, weekdays, negations)
always count and are reported one by one. Runs of ordinary words are joined.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .lookalike import is_lookalike
from .tokenize import Token, tokenize


@dataclass(frozen=True)
class Diff:
    op: str
    kind: str
    official: str | None
    copy: str | None
    old_span: tuple[int, int]  # token indexes in the COPY (zero-width for a delete)
    new_span: tuple[int, int]  # token indexes in the OFFICIAL text
    lookalike: bool = False  # differs only by look-alike characters: cannot be called an edit
    box: tuple[float, float, float, float] | None = None  # x, y, w, h on a photo (0-1); None for typed text

    def to_change(self) -> dict:
        """The contract Change shape without a box (used for record-to-record changes)."""
        return {"op": self.op, "kind": self.kind, "official": self.official, "copy": self.copy}

    def to_photo_change(self) -> dict:
        """The contract Change shape, with a box when the copy came from a photo."""
        change = self.to_change()
        if self.box is not None:
            change["box"] = [round(v, 4) for v in self.box]
        return change


def _join(tokens: list[Token]) -> str:
    return " ".join(t.text for t in tokens)


def _singles(tokens: list[Token], base: int, op: str, at: int) -> list[tuple[int, Diff]]:
    """Report tokens that exist on one side only. `at` is the position in the other side."""
    out: list[tuple[int, Diff]] = []
    run: list[tuple[int, Token]] = []

    def flush() -> None:
        if not run:
            return
        text = _join([t for _, t in run])
        first, last = run[0][0], run[-1][0] + 1
        out.append((first, _make(op, "text", text, (first, last), at)))
        run.clear()

    for i, tok in enumerate(tokens, start=base):
        if tok.meaningful:
            flush()
            out.append((i, _make(op, tok.kind, tok.text, (i, i + 1), at)))
        else:
            run.append((i, tok))
    flush()
    return out


def _make(op: str, kind: str, text: str, span: tuple[int, int], at: int) -> Diff:
    if op == "insert":  # words only in the copy
        return Diff("insert", kind, None, text, span, (at, at))
    return Diff("delete", kind, text, None, (at, at), span)  # words only in the official text


def _pair_block(old: list[Token], new: list[Token], i0: int, j0: int) -> list[tuple[int, Diff]]:
    out: list[tuple[int, Diff]] = []
    # A block that differs only by look-alike characters is ONE uncertain difference.
    if old and new and is_lookalike("".join(t.text for t in old), "".join(t.text for t in new)):
        kind = next((t.kind for t in new if t.meaningful), "text")
        return [
            (i0, Diff("replace", kind, _join(new), _join(old), (i0, i0 + len(old)), (j0, j0 + len(new)), lookalike=True))
        ]
    old_m = [(i0 + n, t) for n, t in enumerate(old) if t.meaningful]
    new_m = [(j0 + n, t) for n, t in enumerate(new) if t.meaningful]

    # 1. same-kind meaningful tokens pair up in order
    used_old: set[int] = set()
    used_new: set[int] = set()
    for kind in dict.fromkeys(t.kind for _, t in old_m):
        olds = [(i, t) for i, t in old_m if t.kind == kind]
        news = [(j, t) for j, t in new_m if t.kind == kind]
        for (i, a), (j, b) in zip(olds, news):
            out.append((i, Diff("replace", kind, b.text, a.text, (i, i + 1), (j, j + 1))))
            used_old.add(i)
            used_new.add(j)

    # 2. leftover meaningful tokens of different kinds pair up in order (kind of the official side)
    left_old = [(i, t) for i, t in old_m if i not in used_old]
    left_new = [(j, t) for j, t in new_m if j not in used_new]
    for (i, a), (j, b) in zip(left_old, left_new):
        out.append((i, Diff("replace", b.kind, b.text, a.text, (i, i + 1), (j, j + 1))))
        used_old.add(i)
        used_new.add(j)
    for i, a in left_old:
        if i not in used_old:
            out.append((i, _make("insert", a.kind, a.text, (i, i + 1), j0)))
    for j, b in left_new:
        if j not in used_new:
            out.append((i0, _make("delete", b.kind, b.text, (j, j + 1), i0)))

    # 3. ordinary words: one replace for the run, or an insert / delete
    old_t = [t for t in old if not t.meaningful]
    new_t = [t for t in new if not t.meaningful]
    if old_t and new_t:
        out.append((i0, Diff("replace", "text", _join(new_t), _join(old_t), (i0, i0 + len(old)), (j0, j0 + len(new)))))
    elif old_t:
        out.append((i0, _make("insert", "text", _join(old_t), (i0, i0 + len(old)), j0)))
    elif new_t:
        out.append((i0, _make("delete", "text", _join(new_t), (j0, j0 + len(new)), i0)))
    return out


def diff_tokens(copy: list[Token], official: list[Token]) -> list[Diff]:
    matcher = SequenceMatcher(None, [t.cmp_key for t in copy], [t.cmp_key for t in official], autojunk=False)
    found: list[tuple[int, Diff]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            found += _pair_block(copy[i1:i2], official[j1:j2], i1, j1)
        elif tag == "delete":  # only in the copy
            found += _singles(copy[i1:i2], i1, "insert", j1)
        elif tag == "insert":  # only in the official text
            found += _singles(official[j1:j2], j1, "delete", i1)
    found.sort(key=lambda pair: (pair[0], pair[1].new_span[0]))
    return [d for _, d in found]


def diff_text(copy_text: str, official_text: str) -> list[Diff]:
    return diff_tokens(tokenize(copy_text), tokenize(official_text))
