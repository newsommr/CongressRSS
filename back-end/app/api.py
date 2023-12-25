from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from app.models import RSSItem, CongressInfo
from app.crud import get_db
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Constants for readability and maintainability
CHAMBER_SENATE = "senate"
CHAMBER_HOUSE = "house"
INVALID_LIMIT_DETAIL = "Invalid limit/offset value. Must be > 0"
ITEMS_NOT_FOUND_DETAIL = "Items not found."
INVALID_CHAMBER_DETAIL = "Invalid chamber specified."

router = APIRouter()

# Added docstrings for clarity
@router.get("/items/")
async def read_items(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Get a list of RSS items with pagination.
    """
    if limit <= 0 or offset < 0:
        raise HTTPException(status_code=400, detail=INVALID_LIMIT_DETAIL)

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
async def read_items_by_source(source: str, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Get RSS items by source with pagination.
    """
    if limit <= 0:
        raise HTTPException(status_code=400, detail=INVALID_LIMIT_DETAIL)
    try:
        items = db.query(RSSItem)\
                  .filter(RSSItem.source == source)\
                  .order_by(desc(RSSItem.pubDate))\
                  .limit(limit).all()
        if not items:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/items/search/{search_term}")
async def search_items(search_term: str, sources: str = "", limit: int = None, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Search RSS items by term, with optional source filtering and pagination.
    """
    query = db.query(RSSItem)

    try:
        date_obj = datetime.strptime(search_term, "%B %d, %Y")
        query = query.filter(func.date(RSSItem.pubDate) == date_obj.date())
    except ValueError:
        query = query.filter(RSSItem.title.ilike(f'%{search_term}%'))

    if sources:
        source_list = sources.split(',')
        query = query.filter(RSSItem.source.in_(source_list))

    query = query.order_by(desc(RSSItem.pubDate)).offset(offset)

    if limit is not None:
        if limit <= 0 or offset < 0:
            raise HTTPException(status_code=400, detail=INVALID_LIMIT_DETAIL)
        query = query.limit(limit)

    items = query.all()

    if not items and offset == 0:
        raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)
    return items


@router.get("/info/session/{chamber}")
async def get_congress_session_info(chamber: str, db: AsyncSession = Depends(get_db)):
    """
    Get next meeting information for a specific congressional chamber.
    """
    try:
        session_info = db.query(CongressInfo).first()
        if not session_info:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)

        if chamber == CHAMBER_SENATE:
            return session_info.senate_next_meeting
        elif chamber == CHAMBER_HOUSE:
            return session_info.house_next_meeting
        else:
            raise HTTPException(status_code=400, detail=INVALID_CHAMBER_DETAIL)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
