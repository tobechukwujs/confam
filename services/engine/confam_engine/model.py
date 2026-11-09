from __future__ import annotations

from dataclasses import dataclass


class RecordError(ValueError):
    """The record is inconsistent (a replacement that does not exist, or a cycle)."""


@dataclass(frozen=True)
class Replacement:
    id: str
    published: str  # YYYY-MM-DD


@dataclass(frozen=True)
class OfficialNotice:
    id: str
    title: str
    published: str  # YYYY-MM-DD
    url: str
    text: str
    superseded_by: Replacement | None = None
