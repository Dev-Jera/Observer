from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=list[schemas.ArticleOut])
def list_articles(
    topic: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(models.Article).order_by(models.Article.created_at.desc())
    if topic:
        q = q.filter(models.Article.topic == topic)
    return q.limit(limit).all()


@router.get("/{article_id}", response_model=schemas.ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(models.Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
