"""Notice registry helpers for CivicNotice v0.1.0."""

from __future__ import annotations

from dataclasses import dataclass


DISCLAIMER = (
    "CivicNotice supports statutory notice administration, but staff remain "
    "responsible for deadlines, publication approvals, legal sufficiency, and "
    "the official notice record."
)


@dataclass(frozen=True)
class NoticeRecord:
    notice_id: str
    notice_type: str
    owner: str
    registry_notes: tuple[str, ...]
    disclaimer: str = DISCLAIMER


def register_notice_stub(*, notice_id: str, notice_type: str, owner: str) -> NoticeRecord:
    """Return a deterministic notice registry stub for staff review."""

    notes = (
        "Confirm statutory authority, publication channel, lead time, and responsible reviewer.",
        "Attach source agenda item, bid file, vacancy record, hearing record, or staff memo.",
        "Route draft copy and publication proof through clerk/legal review before release.",
    )
    return NoticeRecord(
        notice_id=notice_id.strip() or "unassigned-notice",
        notice_type=notice_type.strip() or "general notice",
        owner=owner.strip() or "Unassigned owner",
        registry_notes=notes,
    )
