"""Notice archive and handoff packets for CivicNotice v0.1.3."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class NoticeArchivePacket:
    notice_id: str
    notice_type: str
    source_module: str
    source_record_id: str
    evidence_items: tuple[str, ...]
    missing_items: tuple[str, ...]
    handoff_targets: tuple[str, ...]
    readiness_status: str
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def build_notice_archive_packet(
    *,
    notice_id: str,
    notice_type: str,
    source_module: str,
    source_record_id: str,
    registry_record_id: str = "",
    deadline_plan_id: str = "",
    publication_proof_id: str = "",
    rule_check_complete: bool = False,
    template_complete: bool = False,
    accessibility_review_complete: bool = False,
    subscriber_delivery_complete: bool = False,
    records_export_complete: bool = False,
) -> NoticeArchivePacket:
    """Assemble a notice archive/handoff packet for staff review."""

    required_items = {
        "registry record": registry_record_id,
        "deadline plan": deadline_plan_id,
        "publication proof": publication_proof_id,
        "rule check": "complete" if rule_check_complete else "",
        "notice template": "complete" if template_complete else "",
        "accessibility review": "complete" if accessibility_review_complete else "",
        "subscriber delivery plan": "complete" if subscriber_delivery_complete else "",
        "records export checklist": "complete" if records_export_complete else "",
    }
    evidence_items = tuple(
        f"{label}: {value}" for label, value in required_items.items() if value
    )
    missing_items = tuple(label for label, value in required_items.items() if not value)
    readiness_status = (
        "archive_packet_ready_for_staff_final_review"
        if not missing_items
        else "archive_packet_incomplete_staff_review_required"
    )
    return NoticeArchivePacket(
        notice_id=notice_id.strip() or "unassigned-notice",
        notice_type=notice_type.strip() or "general notice",
        source_module=source_module.strip() or "manual",
        source_record_id=source_record_id.strip() or "unlinked source record",
        evidence_items=evidence_items,
        missing_items=missing_items,
        handoff_targets=_handoff_targets(source_module),
        readiness_status=readiness_status,
        staff_review_required=True,
    )


def _handoff_targets(source_module: str) -> tuple[str, ...]:
    normalized = source_module.strip().lower()
    targets = ["civicrecords"]
    if normalized == "civicclerk":
        targets.insert(0, "civicclerk")
    elif normalized == "civicprocure":
        targets.insert(0, "civicprocure")
    elif normalized == "civicboards":
        targets.insert(0, "civicboards")
    else:
        targets.insert(0, "manual staff archive")
    return tuple(targets)
