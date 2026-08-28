from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ArticleOut(BaseModel):
    id: int
    title: str
    category: str
    topic: str
    summary: str
    full_text: str
    jurisdiction: str
    plain_explanation: str
    original_wording: str
    law_citation: str
    amendment_history: str
    source_name: str
    source_url: str
    image_url: str
    rights_impact: str
    dyk_text: str
    sms_text: str
    is_live: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RightOut(BaseModel):
    id: int
    title: str
    description: str
    source_ref: str
    category: str
    article_ref: str

    class Config:
        from_attributes = True


class BillOut(BaseModel):
    id: int
    title: str
    description: str
    stage: str
    current_stage: int
    total_stages: int
    article_ref: str
    topic: str
    source_name: str
    source_url: str
    detected_at: datetime

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    image_url: str
    source_name: str
    source_url: str
    source_reference: str
    source_quote: str
    tag: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SmsSubscriptionIn(BaseModel):
    phone_number: str
    cadence_minutes: int = 30
    language: str = "eng"


class SmsSubscriptionOut(BaseModel):
    phone_number: str
    cadence_minutes: int
    language: str
    is_active: bool

    class Config:
        from_attributes = True


class GuidanceItemOut(BaseModel):
    id: int
    title: str
    category: str
    steps: List[str]
    legal_ref: str

    class Config:
        from_attributes = True


class ProcessedContent(BaseModel):
    """Output of the AI processing pipeline for one scraped item."""
    title: str
    summary: str
    full_text: str
    topic: str
    rights_impact: str
    dyk_text: str
    sms_text: str


class ScrapeResult(BaseModel):
    checked_sources: int
    new_items: int
    skipped_duplicates: int
    errors: List[str] = []
