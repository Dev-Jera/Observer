from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/guidance", tags=["guidance"])


@router.get("", response_model=list[schemas.GuidanceItemOut])
def list_guidance(db: Session = Depends(get_db)):
    return db.query(models.GuidanceItem).order_by(models.GuidanceItem.id).all()
