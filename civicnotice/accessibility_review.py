"""Accessibility and language-readiness review for CivicNotice v0.2.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class NoticeAccessibilityReview:
    notice_id: str
    title: str
    missing_accessibility_items: tuple[str, ...]
    plain_language_flags: tuple[str, ...]
    translation_tasks: tuple[str, ...]
    attachment_review_required: bool
    staff_review_required: bool
    review_notes: tuple[str, ...]
    disclaimer: str = DISCLAIMER


def build_accessibility_review(
    *,
    notice_id: str,
    title: str,
    notice_text: str,
    target_languages: tuple[str, ...] = (),
    attachments: tuple[str, ...] = (),
    has_contact: bool = False,
    has_event_date: bool = False,
    has_plain_language_summary: bool = False,
) -> NoticeAccessibilityReview:
    """Build a deterministic public-notice accessibility readiness packet."""

    missing_items = []
    if not has_contact:
        missing_items.append("public contact for accommodations or questions")
    if not has_event_date:
        missing_items.append("clear event, deadline, or effective date")
    if not has_plain_language_summary:
        missing_items.append("plain-language summary for public readers")
    plain_language_flags = _plain_language_flags(notice_text)
    normalized_languages = tuple(
        language.strip() for language in target_languages if language.strip()
    )
    translation_tasks = tuple(
        f"Prepare human-approved {language} notice version or language-access note."
        for language in normalized_languages
        if language.lower() not in {"english", "en"}
    )
    attachment_review_required = bool(attachments)
    staff_review_required = bool(
        missing_items or plain_language_flags or translation_tasks or attachment_review_required
    )
    notes = (
        "This packet prepares staff review before public posting; it does not certify ADA, WCAG, or language-access compliance.",
        "CivicAccess integration and live translation workflows are not active in this release.",
        "Preserve the approved accessible notice version with the proof-of-publication record.",
    )
    return NoticeAccessibilityReview(
        notice_id=notice_id.strip() or "unassigned-notice",
        title=title.strip() or "Untitled notice",
        missing_accessibility_items=tuple(missing_items),
        plain_language_flags=plain_language_flags,
        translation_tasks=translation_tasks,
        attachment_review_required=attachment_review_required,
        staff_review_required=staff_review_required,
        review_notes=notes,
    )


def _plain_language_flags(notice_text: str) -> tuple[str, ...]:
    flags = []
    text = notice_text.strip()
    if not text:
        return ("notice text missing",)
    sentences = [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()]
    if any(len(sentence) > 180 for sentence in sentences):
        flags.append("long sentence review")
    jargon_terms = ("hereinafter", "pursuant to", "aforementioned", "whereas")
    if any(term in text.lower() for term in jargon_terms):
        flags.append("legal or technical jargon review")
    if len(text.split()) > 250:
        flags.append("summary length review")
    return tuple(flags)
