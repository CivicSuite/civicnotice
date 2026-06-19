"""Notice drafting templates for CivicNotice v0.1.3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from civicnotice.notice_registry import DISCLAIMER
from civicnotice.statutory_rules import RULE_PACKS


@dataclass(frozen=True)
class NoticeTemplate:
    notice_type: str
    title: str
    source_module: str
    template_lines: tuple[str, ...]
    required_fields: tuple[str, ...]
    placeholders_remaining: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def build_notice_template(
    *,
    notice_type: str,
    matter_title: str,
    event_date: date,
    location: str,
    contact: str,
    source_module: str = "manual",
    statutory_basis: str = "",
) -> NoticeTemplate:
    """Build a staff-editable notice template without declaring it legally sufficient."""

    rule = RULE_PACKS.get(_clean(notice_type), RULE_PACKS["general notice"])
    clean_title = matter_title.strip() or "Untitled notice matter"
    clean_location = location.strip() or "[staff must enter location]"
    clean_contact = contact.strip() or "[staff must enter contact]"
    clean_basis = statutory_basis.strip() or "[staff must enter statutory basis]"
    placeholders = tuple(
        value
        for value in (clean_location, clean_contact, clean_basis)
        if value.startswith("[staff must enter")
    )
    lines = (
        f"NOTICE: {clean_title}",
        f"Notice type: {rule.notice_type}.",
        f"Event or deadline date: {event_date.isoformat()}.",
        f"Location or submission path: {clean_location}.",
        f"Staff contact: {clean_contact}.",
        f"Statutory basis: {clean_basis}.",
        "Staff must verify required publication channels, lead time, accessibility, and proof before release.",
    )
    return NoticeTemplate(
        notice_type=rule.notice_type,
        title=clean_title,
        source_module=source_module.strip() or "manual",
        template_lines=lines,
        required_fields=rule.required_content,
        placeholders_remaining=placeholders,
        staff_review_required=True,
    )


def _clean(value: str) -> str:
    return " ".join(value.strip().lower().split())
