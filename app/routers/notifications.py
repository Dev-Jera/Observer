from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..services.sms import VALID_CADENCES, normalize_phone, queue_notification_for_subscriber

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    return (
        db.query(models.Notification)
        .order_by(models.Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
    return {"ok": True}


@router.post("/subscribe", response_model=schemas.SmsSubscriptionOut)
def subscribe_to_sms(payload: schemas.SmsSubscriptionIn, db: Session = Depends(get_db)):
    if payload.cadence_minutes not in VALID_CADENCES:
        raise HTTPException(status_code=422, detail="Choose 30, 60, or 360 minutes")
    try:
        phone_number = normalize_phone(payload.phone_number)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    subscriber = db.query(models.SmsSubscriber).filter_by(phone_number=phone_number).first()
    if subscriber:
        subscriber.is_active = True
        subscriber.cadence_minutes = payload.cadence_minutes
    else:
        subscriber = models.SmsSubscriber(
            phone_number=phone_number,
            cadence_minutes=payload.cadence_minutes,
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
