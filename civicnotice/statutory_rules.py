"""Deterministic statutory notice rule checks for CivicNotice v0.1.3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class NoticeRule:
    notice_type: str
    minimum_lead_days: int
    required_publications: int
    required_channels: tuple[str, ...]
    required_content: tuple[str, ...]
    emergency_path_allowed: bool = False


@dataclass(frozen=True)
class StatutoryRuleCheck:
    notice_type: str
    event_date: date
    required_deadline_date: date
    publication_dates: tuple[date, ...]
    channels: tuple[str, ...]
    required_publications: int
    required_channels: tuple[str, ...]
    missing_channels: tuple[str, ...]
    required_content: tuple[str, ...]
    missing_content: tuple[str, ...]
    statutory_basis: str
    deadline_status: str
    publication_count_status: str
    staff_review_required: bool
    disclaimer: str = DISCLAIMER


RULE_PACKS: dict[str, NoticeRule] = {
    "general notice": NoticeRule(
        notice_type="general notice",
        minimum_lead_days=0,
        required_publications=1,
        required_channels=(),
        required_content=("title", "event date", "location", "statutory basis"),
    ),
    "planning hearing": NoticeRule(
        notice_type="planning hearing",
        minimum_lead_days=15,
        required_publications=1,
        required_channels=("city website", "posting board"),
        required_content=("title", "hearing date", "location", "case number", "statutory basis"),
    ),
    "bid notice": NoticeRule(
        notice_type="bid notice",
        minimum_lead_days=14,
        required_publications=1,
        required_channels=("city website", "newspaper"),
        required_content=("title", "bid deadline", "scope summary", "submission location"),
    ),
    "vacancy notice": NoticeRule(
        notice_type="vacancy notice",
        minimum_lead_days=10,
        required_publications=1,
        required_channels=("city website", "posting board"),
        required_content=("title", "office", "application deadline", "eligibility summary"),
    ),
    "adoption notice": NoticeRule(
        notice_type="adoption notice",
        minimum_lead_days=5,
        required_publications=1,
        required_channels=("city website",),
        required_content=("title", "adopted action", "effective date", "inspection location"),
    ),
    "special meeting": NoticeRule(
        notice_type="special meeting",
        minimum_lead_days=2,
        required_publications=1,
        required_channels=("city website", "posting board"),
        required_content=("title", "meeting date", "location", "statutory basis"),
        emergency_path_allowed=True,
    ),
}


def check_statutory_notice_requirements(
    *,
    notice_type: str,
    event_date: date,
    publication_dates: tuple[date, ...] = (),
    channels: tuple[str, ...] = (),
    content_fields: tuple[str, ...] = (),
    statutory_basis: str = "",
) -> StatutoryRuleCheck:
    """Check a notice packet against deterministic staff-review rules."""

    rule = _rule_for(notice_type)
    normalized_channels = tuple(_clean(value) for value in channels if _clean(value))
    normalized_content = tuple(_clean(value) for value in content_fields if _clean(value))
    required_deadline = event_date - timedelta(days=rule.minimum_lead_days)
    missing_channels = tuple(
        channel for channel in rule.required_channels if channel not in normalized_channels
    )
    missing_content = tuple(
        field for field in rule.required_content if field not in normalized_content
    )
    deadline_status = _deadline_status(
        publication_dates=publication_dates,
        required_deadline=required_deadline,
    )
    publication_count_status = (
        "required_publication_count_met"
        if len(publication_dates) >= rule.required_publications
        else "publication_count_staff_review_required"
    )
    basis_missing = "statutory basis" in rule.required_content and not statutory_basis.strip()
    staff_review_required = bool(
        missing_channels
        or missing_content
        or basis_missing
        or deadline_status != "meets_minimum_lead_time"
        or publication_count_status != "required_publication_count_met"
    )
    return StatutoryRuleCheck(
        notice_type=rule.notice_type,
        event_date=event_date,
        required_deadline_date=required_deadline,
        publication_dates=publication_dates,
        channels=normalized_channels,
        required_publications=rule.required_publications,
        required_channels=rule.required_channels,
        missing_channels=missing_channels,
        required_content=rule.required_content,
        missing_content=missing_content,
        statutory_basis=statutory_basis.strip() or "staff-provided statutory basis required",
        deadline_status=deadline_status,
        publication_count_status=publication_count_status,
        staff_review_required=staff_review_required,
    )


def _rule_for(notice_type: str) -> NoticeRule:
    normalized = _clean(notice_type)
    return RULE_PACKS.get(normalized, RULE_PACKS["general notice"])


def _deadline_status(*, publication_dates: tuple[date, ...], required_deadline: date) -> str:
    if not publication_dates:
        return "publication_schedule_missing_staff_review_required"
    latest_publication = max(publication_dates)
    if latest_publication <= required_deadline:
        return "meets_minimum_lead_time"
    return "deadline_risk_staff_review_required"


def _clean(value: str) -> str:
    return " ".join(value.strip().lower().split())
