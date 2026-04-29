"""Publication deadline helpers for CivicNotice v0.1.2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from civiccore.notifications import build_deadline_plan as build_civiccore_deadline_plan
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

    shared_plan = build_civiccore_deadline_plan(
        notice_type=notice_type,
        event_date=event_date,
        lead_days=lead_days,
    )
    return DeadlinePlan(
        notice_type=shared_plan.notice_type,
        event_date=shared_plan.event_date,
        reminders=shared_plan.reminders,
        staff_review_required=shared_plan.staff_review_required,
    )
