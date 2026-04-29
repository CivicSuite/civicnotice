"""Notice channel planning helpers for CivicNotice v0.1.2."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class ChannelPlan:
    notice_type: str
    channels: tuple[str, ...]
    accessibility_notes: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def plan_notice_channels(*, notice_type: str, audience: str) -> ChannelPlan:
    """Suggest review channels without publishing official notice."""

    channels = (
        "official posting board or website",
        "newspaper or legal publication if required",
        "agenda/packet page when tied to a meeting",
        "accessible alternate format review",
    )
    notes = (
        f"Audience context: {audience.strip() or 'general public'}.",
        "Staff must verify language access, ADA format, and statutory publication requirements.",
    )
    return ChannelPlan(
        notice_type=notice_type.strip() or "general notice",
        channels=channels,
        accessibility_notes=notes,
        staff_review_required=True,
    )
