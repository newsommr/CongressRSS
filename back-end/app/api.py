from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from app.database import get_db, RSSItem
import logging
from datetime import datetime

router = APIRouter()

@router.get("/items/")
def read_items(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        items = db.query(RSSItem)\
            .order_by(desc(RSSItem.pubDate))\
            .offset(offset)\
            .limit(limit)\
            .all()
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

@router.get("/items/search/{search_term}")
def search_items(search_term: str, sources: str = "", limit: int = None, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(RSSItem)

    # Determine if search_term is a date
    try:
        date_obj = datetime.strptime(search_term, "%B %d, %Y")
        query = query.filter(func.date(RSSItem.pubDate) == date_obj.date())
    except ValueError:
        # If not a date, search in title
        query = query.filter(RSSItem.title.ilike(f'%{search_term}%'))

    # Apply source filter if provided
    if sources:
        source_list = sources.split(',')
        query = query.filter(RSSItem.source.in_(source_list))

    query = query.order_by(desc(RSSItem.pubDate)).offset(offset)

    # Apply limit only if provided
    if limit is not None and limit > 0:
        query = query.limit(limit)
    elif limit is not None and limit <= 0:
        raise HTTPException(status_code=400, detail="Invalid limit value. Must be > 0")

    items = query.all()

    if not items and offset == 0:
        raise HTTPException(status_code=404, detail="Items not found.")
    return items


