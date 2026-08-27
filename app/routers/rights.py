from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/rights", tags=["rights"])


@router.get("", response_model=list[schemas.RightOut])
def list_rights(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(models.Right).order_by(models.Right.title)
    if category:
        q = q.filter(models.Right.category == category)
    return q.all()
