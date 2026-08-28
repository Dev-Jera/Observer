"""Africa's Talking SMS delivery, disabled cleanly when credentials are absent."""
import logging
import re

import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from ..config import settings
from .. import models

logger = logging.getLogger("citizeneye.sms")
SMS_URL = "https://api.africastalking.com/version1/messaging"
SUNBIRD_URL = "https://api.sunbird.ai/tasks/translate"
UGANDA_PHONE = re.compile(r"^\+256\d{9}$")
VALID_CADENCES = (1, 5, 30, 60, 360)


def normalize_phone(phone_number: str) -> str:
    """Normalize common Ugandan phone input to Africa's Talking E.164 format."""
    value = re.sub(r"[\s()-]", "", phone_number)
    if value.startswith("07") or value.startswith("03"):
        value = "+256" + value[1:]
    elif value.startswith("256"):
        value = "+" + value
    if not UGANDA_PHONE.fullmatch(value):
        raise ValueError("Enter a valid Ugandan phone number, for example +256701234567")
    return value


def queue_notification(db: Session, notification: models.Notification) -> None:
    """Queue a notification for each active subscriber at their next send time."""
    now = datetime.now(timezone.utc)
    subscribers = db.query(models.SmsSubscriber).filter_by(is_active=True).all()
    for subscriber in subscribers:
        scheduled_for = subscriber.next_delivery_at or now
        if scheduled_for.tzinfo is None:
            scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
        db.add(models.SmsDelivery(
            subscriber_id=subscriber.id,
            notification_id=notification.id,
            scheduled_for=max(now, scheduled_for),
        ))


def queue_notification_for_subscriber(
    db: Session, notification: models.Notification, subscriber: models.SmsSubscriber
) -> None:
    """Queue one notification for a newly subscribed recipient."""
    now = datetime.now(timezone.utc)
    scheduled_for = subscriber.next_delivery_at or now
    if scheduled_for.tzinfo is None:
        scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
    db.add(models.SmsDelivery(
        subscriber_id=subscriber.id,
        notification_id=notification.id,
        scheduled_for=max(now, scheduled_for),
    ))


def deliver_due_sms(db: Session) -> int:
    """Send queued notifications that have reached each subscriber's cadence."""
    now = datetime.now(timezone.utc)
    sent_count = 0
    subscribers = db.query(models.SmsSubscriber).filter_by(is_active=True).all()
    for subscriber in subscribers:
        due = (
            db.query(models.SmsDelivery)
            .filter(
                models.SmsDelivery.subscriber_id == subscriber.id,
                models.SmsDelivery.sent_at.is_(None),
                models.SmsDelivery.scheduled_for <= now,
            )
            .order_by(models.SmsDelivery.scheduled_for, models.SmsDelivery.id)
            .limit(10)
            .all()
        )
        if not due:
            continue
        notifications = [db.get(models.Notification, item.notification_id) for item in due]
        messages = [translate_text(n.sms_text or n.message, subscriber.language) for n in notifications if n]
        message = " ".join(messages)[:160]
        sent, delivery_error = send_sms([subscriber.phone_number], message)
        if sent:
            for item in due:
                item.sent_at = now
                item.error = ""
            subscriber.next_delivery_at = now + timedelta(minutes=subscriber.cadence_minutes)
            sent_count += 1
        else:
            for item in due:
                item.error = delivery_error
    db.commit()
    return sent_count


def translate_text(text: str, target_language: str) -> str:
    if not text or target_language == "eng" or not settings.sunbird_api_key:
        return text
    try:
        response = httpx.post(
            SUNBIRD_URL,
            json={"source_language": "eng", "target_language": target_language, "text": text},
            headers={"Authorization": f"Bearer {settings.sunbird_api_key}"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("output", {}).get("translated_text") or text
    except (httpx.HTTPError, ValueError, TypeError):
        logger.exception("Sunbird translation failed for %s", target_language)
        return text


def send_sms(phone_numbers: list[str], message: str) -> tuple[bool, str]:
    """Send one SMS batch and return a useful provider error when rejected."""
    if not phone_numbers:
        return True, ""
    if not settings.africastalking_username or not settings.africastalking_api_key:
        logger.info("Africa's Talking is not configured; SMS delivery skipped")
        return False, "Africa's Talking credentials are not configured"

    data = {
        "username": settings.africastalking_username,
        "to": ",".join(phone_numbers),
        "message": message[:160],
    }
    if settings.africastalking_sender_id:
        data["from"] = settings.africastalking_sender_id
    try:
        response = httpx.post(
            SMS_URL,
            data=data,
            headers={"apiKey": settings.africastalking_api_key, "Accept": "application/json"},
            timeout=20,
        )
        response.raise_for_status()
        return True, ""
    except httpx.HTTPStatusError as exc:
        provider_error = f"Africa's Talking HTTP {exc.response.status_code}: {exc.response.text[:500]}"
        logger.error(provider_error)
        return False, provider_error
    except httpx.RequestError as exc:
        provider_error = f"Africa's Talking request error: {exc}"
        logger.error(provider_error)
        return False, provider_error