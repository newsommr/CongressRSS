from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, RSSItem

router = APIRouter()

@router.get("/items/")
def read_items(limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(RSSItem)\
        .order_by(desc(RSSItem.pubDate))\
        .limit(limit).all()
    return items

@router.get("/items/{source}")
def read_items_by_source(source: str, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(RSSItem)\
              .filter(RSSItem.source == source)\
              .order_by(desc(RSSItem.pubDate))\
              .limit(limit).all()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return items
