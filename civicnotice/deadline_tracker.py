"""Publication deadline helpers for CivicNotice v0.1.0."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class DeadlinePlan:
    notice_type: str
    event_date: date
    reminders: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


def build_deadline_plan(*, notice_type: str, event_date: date, lead_days: int = 10) -> DeadlinePlan:
    """Build deterministic publication reminders without declaring legal sufficiency."""

    publish_by = event_date - timedelta(days=lead_days)
    reminders = (
        f"{publish_by - timedelta(days=14)}: confirm statutory authority and publication channel.",
        f"{publish_by - timedelta(days=7)}: route draft copy for clerk/legal review.",
        f"{publish_by}: publish or file proof of publication deadline.",
        f"{event_date}: verify final notice packet before hearing/opening/action.",
    )
    return DeadlinePlan(
        notice_type=notice_type.strip() or "general notice",
        event_date=event_date,
        reminders=reminders,
        staff_review_required=True,
    )
