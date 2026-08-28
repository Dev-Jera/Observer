from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..services.sms import VALID_CADENCES, normalize_phone, queue_notification_for_subscriber, translate_text

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationOut])
def list_notifications(language: str = Query("eng"), topics: str = Query(""), db: Session = Depends(get_db)):
    notifications = (
        db.query(models.Notification)
        .order_by(models.Notification.created_at.desc())
        .limit(50)
        .all()
    )
    if language not in {"eng", "lug", "ach", "nyn", "lug_UG", "teo"}:
        language = "eng"
    selected_topics = {topic.strip().lower() for topic in topics.split(",") if topic.strip()}
    if selected_topics:
        notifications = [item for item in notifications if item.tag.lower() in selected_topics]
    return [
        {
            "id": item.id,
            "title": translate_text(item.title, language),
            "message": translate_text(item.message, language),
            "image_url": item.image_url,
            "source_name": item.source_name,
            "source_url": item.source_url,
            "source_reference": item.source_reference,
            "source_quote": item.source_quote,
            "tag": item.tag,
            "is_read": item.is_read,
            "created_at": item.created_at,
        }
        for item in notifications
    ]


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
    return {"ok": True}


@router.post("/subscribe", response_model=schemas.SmsSubscriptionOut)
def subscribe_to_sms(payload: schemas.SmsSubscriptionIn, db: Session = Depends(get_db)):
    if payload.cadence_minutes not in VALID_CADENCES:
        raise HTTPException(status_code=422, detail="Choose 1, 5, 30, 60, or 360 minutes")
    try:
        phone_number = normalize_phone(payload.phone_number)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    subscriber = db.query(models.SmsSubscriber).filter_by(phone_number=phone_number).first()
    language = payload.language if payload.language in {"eng", "lug", "ach", "nyn", "lug_UG", "teo"} else "eng"
    if subscriber:
        subscriber.is_active = True
        subscriber.cadence_minutes = payload.cadence_minutes
        subscriber.language = language
    else:
        subscriber = models.SmsSubscriber(
            phone_number=phone_number,
            cadence_minutes=payload.cadence_minutes,
            language=language,
            is_active=True,
        )
        db.add(subscriber)
    db.flush()
    latest_unread = (
        db.query(models.Notification)
        .filter_by(is_read=False)
        .order_by(models.Notification.created_at.desc())
        .first()
    )
    if latest_unread:
        already_queued = db.query(models.SmsDelivery).filter_by(
            subscriber_id=subscriber.id,
            notification_id=latest_unread.id,
        ).first()
        if not already_queued:
            queue_notification_for_subscriber(db, latest_unread, subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.delete("/subscribe/{phone_number}")
def unsubscribe_from_sms(phone_number: str, db: Session = Depends(get_db)):
    try:
        normalized = normalize_phone(phone_number)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    subscriber = db.query(models.SmsSubscriber).filter_by(phone_number=normalized).first()
    if subscriber:
        subscriber.is_active = False
        db.commit()
    return {"ok": True}
