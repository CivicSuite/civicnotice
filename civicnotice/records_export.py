"""Notice records export helpers for CivicNotice v0.1.2."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class NoticeRecordsExport:
    notice_id: str
    title: str
    checklist: tuple[str, ...]
    retention_note: str
    disclaimer: str = DISCLAIMER


def build_notice_records_export(
    *, notice_id: str, title: str, format: str = "markdown"
) -> NoticeRecordsExport:
    """Return a public-records-aware notice export checklist."""

    checklist = (
        "Preserve draft notice, final notice, approval record, publication proof, and source matter.",
        "Confirm confidential, privileged, or closed-session material is excluded before release.",
        "Include file hashes, export timestamp, notice identifier, channel, and reviewer initials.",
        "Record whether the export is for public portal, records request, or staff archive.",
    )
    return NoticeRecordsExport(
        notice_id=notice_id.strip() or "unassigned-notice",
        title=title.strip() or "Notice records export",
        checklist=checklist,
        retention_note=f"Export format '{format}' must follow the city's retention schedule.",
    )
