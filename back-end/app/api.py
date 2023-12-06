from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, RSSItem
import logging

router = APIRouter()

@router.get("/items/")
def read_items(limit: int = 100, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Invalid limit value. Must be > 0")
    try:
        items = db.query(RSSItem)\
            .order_by(desc(RSSItem.pubDate))\
            .limit(limit).all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/items/{source}")
def read_items_by_source(source: str, limit: int = 100, db: Session = Depends(get_db)):
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Invalid limit value. Must be > 0")
    try:
        items = db.query(RSSItem)\
                  .filter(RSSItem.source == source)\
                  .order_by(desc(RSSItem.pubDate))\
                  .limit(limit).all()
        if not items:
            raise HTTPException(status_code=404, detail="Items not found.")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
