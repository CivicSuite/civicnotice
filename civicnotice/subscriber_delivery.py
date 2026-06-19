"""Subscriber delivery planning for CivicNotice v0.2.0."""

from __future__ import annotations

from dataclasses import dataclass

from civicnotice.notice_registry import DISCLAIMER


@dataclass(frozen=True)
class Subscriber:
    subscriber_id: str
    name: str
    email: str
    channels: tuple[str, ...]
    language: str
    active: bool = True


@dataclass(frozen=True)
class SubscriberDeliveryPlan:
    notice_id: str
    notice_type: str
    audience: str
    active_subscriber_count: int
    suppressed_subscriber_count: int
    delivery_channels: tuple[str, ...]
    email_recipients: tuple[str, ...]
    missing_required_channels: tuple[str, ...]
    language_review_required: bool
    staff_review_required: bool
    delivery_notes: tuple[str, ...]
    disclaimer: str = DISCLAIMER


def build_subscriber_delivery_plan(
    *,
    notice_id: str,
    notice_type: str,
    audience: str,
    subscribers: tuple[Subscriber, ...],
    required_channels: tuple[str, ...] = ("email",),
) -> SubscriberDeliveryPlan:
    """Build a staff-reviewable subscriber delivery plan without sending notices."""

    active_subscribers = tuple(subscriber for subscriber in subscribers if subscriber.active)
    suppressed_count = len(subscribers) - len(active_subscribers)
    normalized_required = tuple(_clean(channel) for channel in required_channels if _clean(channel))
    channel_set = {
        channel
        for subscriber in active_subscribers
        for channel in subscriber.channels
        if _clean(channel)
    }
    normalized_channels = tuple(sorted(_clean(channel) for channel in channel_set))
    email_recipients = tuple(
        sorted(
            {
                subscriber.email.strip().lower()
                for subscriber in active_subscribers
                if subscriber.email.strip()
                and "email" in {_clean(channel) for channel in subscriber.channels}
            }
        )
    )
    languages = {_clean(subscriber.language) for subscriber in active_subscribers if subscriber.language}
    missing_required = tuple(
        channel for channel in normalized_required if channel not in normalized_channels
    )
    language_review_required = bool(languages - {"", "english", "en"})
    staff_review_required = bool(missing_required or language_review_required)
    notes = (
        "Delivery plan only prepares recipients and channels; it does not send or publish notices.",
        "Staff must verify opt-in status, suppression lists, bounced addresses, and legal delivery requirements.",
        "Preserve delivery logs or third-party confirmations with the publication proof packet.",
    )
    return SubscriberDeliveryPlan(
        notice_id=notice_id.strip() or "unassigned-notice",
        notice_type=notice_type.strip() or "general notice",
        audience=audience.strip() or "general public",
        active_subscriber_count=len(active_subscribers),
        suppressed_subscriber_count=suppressed_count,
        delivery_channels=normalized_channels,
        email_recipients=email_recipients,
        missing_required_channels=missing_required,
        language_review_required=language_review_required,
        staff_review_required=staff_review_required,
        delivery_notes=notes,
    )


def _clean(value: str) -> str:
    return " ".join(value.strip().lower().split())
