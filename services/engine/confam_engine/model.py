from __future__ import annotations

from dataclasses import dataclass


class RecordError(ValueError):
    """The record is inconsistent (a replacement that does not exist, or a cycle)."""


@dataclass(frozen=True)
class Replacement:
    id: str
    published: str  # YYYY-MM-DD


@dataclass(frozen=True)
class Signature:
    reviewer: str
    role: str  # "first" or "second"
    signed_at: str  # ISO timestamp


@dataclass(frozen=True)
class OfficialNotice:
    id: str
    title: str
    published: str  # YYYY-MM-DD
    url: str  # the source address given by the record; may not be a real, reachable site
    text: str
    superseded_by: Replacement | None = None
    lang: str = "en"  # language the notice is written in; quoted word for word in it
    signatures: tuple[Signature, ...] = ()
