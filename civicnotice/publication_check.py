"""Publication-readiness checks for CivicNotice v0.1.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class PublicationChecklist:
    notice_type: str
    checklist: tuple[str, ...]
    proof_required: bool
    disclaimer: str = DISCLAIMER


def build_publication_checklist(*, notice_type: str, channel: str) -> PublicationChecklist:
    """Return a staff-owned publication-readiness checklist."""

    items = (
        "Confirm notice title, body, date/time/place, affected matter, and statutory citation.",
        f"Confirm publication channel '{channel.strip() or 'unspecified'}' is authorized.",
        "Verify lead time, posting location, language/accessibility needs, and proof requirements.",
        "Preserve draft, approval, publication proof, screenshots, invoices, and final packet.",
    )
    return PublicationChecklist(
        notice_type=notice_type.strip() or "general notice",
        checklist=items,
        proof_required=True,
    )
