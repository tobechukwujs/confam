"""Rule 2: work out what replaced a notice and how it differs."""

from __future__ import annotations

from collections.abc import Sequence

from .compare import diff_text
from .model import OfficialNotice, RecordError


def latest_successor(notice: OfficialNotice, record: Sequence[OfficialNotice]) -> OfficialNotice | None:
    """Follow `superseded_by` to the newest notice. None if the notice is current."""
    by_id = {n.id: n for n in record}
    seen = {notice.id}
    current = notice
    while current.superseded_by is not None:
        next_id = current.superseded_by.id
        if next_id in seen:
            raise RecordError(f"Replacement cycle at {next_id}")
        nxt = by_id.get(next_id)
        if nxt is None:
            raise RecordError(f"{current.id} is replaced by {next_id}, which is not in the record")
        seen.add(next_id)
        current = nxt
    return None if current is notice else current


def supersession_for(notice: OfficialNotice, record: Sequence[OfficialNotice]) -> dict | None:
    """The contract `superseded_by` object for a matched notice, or None if it is current.

    `changes`: official = value in the NEW notice, copy = value in the OLD (matched) notice.
    """
    newest = latest_successor(notice, record)
    if newest is None:
        return None
    return {
        "id": newest.id,
        "published": newest.published,
        "url": newest.url,
        "title": newest.title,
        "changes": [d.to_change() for d in diff_text(notice.text, newest.text)],
    }
