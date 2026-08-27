from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/bills", tags=["bills"])


@router.get("", response_model=list[schemas.BillOut])
def list_bills(topic: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(models.Bill).order_by(models.Bill.detected_at.desc())
    if topic:
        q = q.filter(models.Bill.topic == topic)
    return q.all()
