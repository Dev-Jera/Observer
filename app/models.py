from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(100), default="PARLIAMENT")
    topic: Mapped[str] = mapped_column(String(100), default="general")
    summary: Mapped[str] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text, default="")
    jurisdiction: Mapped[str] = mapped_column(String(100), default="Uganda")
    plain_explanation: Mapped[str] = mapped_column(Text, default="")
    original_wording: Mapped[str] = mapped_column(Text, default="")
    law_citation: Mapped[str] = mapped_column(String(500), default="")
    amendment_history: Mapped[str] = mapped_column(Text, default="")
    source_name: Mapped[str] = mapped_column(String(300))
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    rights_impact: Mapped[str] = mapped_column(String(500), default="")
    dyk_text: Mapped[str] = mapped_column(Text, default="")
    sms_text: Mapped[str] = mapped_column(Text, default="")
    is_live: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Right(Base):
    __tablename__ = "rights"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    source_ref: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(50), index=True)
    article_ref: Mapped[str] = mapped_column(String(200), default="")


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(100))
    current_stage: Mapped[int] = mapped_column(Integer, default=1)
    total_stages: Mapped[int] = mapped_column(Integer, default=4)
    article_ref: Mapped[str] = mapped_column(String(200), default="")
    topic: Mapped[str] = mapped_column(String(100), default="general")
    source_name: Mapped[str] = mapped_column(String(300), default="")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(Text)
    sms_text: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(1000), default="")
    tag: Mapped[str] = mapped_column(String(100), default="ALERT")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SmsSubscriber(Base):
    __tablename__ = "sms_subscribers"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    cadence_minutes: Mapped[int] = mapped_column(Integer, default=30)
    language: Mapped[str] = mapped_column(String(20), default="eng")
    next_delivery_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SmsDelivery(Base):
    __tablename__ = "sms_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("sms_subscribers.id"), index=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"), index=True)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str] = mapped_column(Text, default="")


class GuidanceItem(Base):
    __tablename__ = "guidance_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(100))
    steps: Mapped[list] = mapped_column(JSON)
    legal_ref: Mapped[str] = mapped_column(String(300))


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(1000))
    kind: Mapped[str] = mapped_column(String(50))  # parliament | government | legal
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class SeenContent(Base):
    __tablename__ = "seen_content"

    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(500))
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
