"""Publication proof workpaper helpers for CivicNotice v0.2.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class PublicationProof:
    notice_id: str
    notice_type: str
    source_module: str
    source_record_id: str
    channel: str
    published_at: str
    location: str
    confirmation_reference: str
    statutory_basis: str
    reviewer: str
    proof_notes: tuple[str, ...]
    compliance_status: str
    disclaimer: str = DISCLAIMER


def record_publication_proof(
    *,
    notice_id: str,
    notice_type: str,
    source_module: str,
    source_record_id: str,
    channel: str,
    published_at: str,
    location: str,
    confirmation_reference: str,
    statutory_basis: str,
    reviewer: str,
) -> PublicationProof:
    """Return a staff-owned publication proof packet for durable storage."""

    clean_channel = channel.strip() or "unspecified channel"
    clean_location = location.strip() or "unspecified location"
    clean_reference = confirmation_reference.strip() or "pending confirmation reference"
    clean_basis = statutory_basis.strip() or "staff-provided statutory basis required"
    clean_reviewer = reviewer.strip() or "staff review required"
    proof_notes = (
        f"Preserve proof from {clean_channel} at {clean_location}.",
        f"Link confirmation reference: {clean_reference}.",
        f"Staff must verify statutory basis before relying on this packet: {clean_basis}.",
        "This packet stores evidence for staff review; it does not certify legal sufficiency or publish an official notice.",
    )
    return PublicationProof(
        notice_id=notice_id.strip() or "unassigned notice",
        notice_type=notice_type.strip() or "general notice",
        source_module=source_module.strip() or "manual",
        source_record_id=source_record_id.strip() or "unlinked source record",
        channel=clean_channel,
        published_at=published_at.strip() or "pending publication timestamp",
        location=clean_location,
        confirmation_reference=clean_reference,
        statutory_basis=clean_basis,
        reviewer=clean_reviewer,
        proof_notes=proof_notes,
        compliance_status="proof_recorded_staff_review_required",
    )
