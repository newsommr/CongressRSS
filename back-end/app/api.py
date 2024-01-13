from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from app.models import RSSItem, SenateInfo, HouseInfo
from app.crud import get_db
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Constants for readability and maintainability
CHAMBER_SENATE = "senate"
CHAMBER_HOUSE = "house"
INVALID_LIMIT_DETAIL = "Invalid limit/offset value. Must be > 0"
ITEMS_NOT_FOUND_DETAIL = "Items not found"
INVALID_CHAMBER_DETAIL = "Invalid chamber specified"
INTERNAL_SERVER_ERROR = "Internal server error"

router = APIRouter()

def validate_pagination(limit, offset):
    """ 
    Validates the limit and offset for pagination
    """
    if limit <= 0 or offset < 0:
        raise HTTPException(status_code=400, detail=INVALID_LIMIT_DETAIL)

@router.get("/items/search/")
async def search_items(search_term: str = "", sources: str = "", limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Search RSS items by term, with optional source filtering and pagination.
    """
    validate_pagination(limit, offset)

    try:
        query = db.query(RSSItem)

        # Apply source filtering if sources are provided
        if sources:
            source_list = sources.split(',')
            query = query.filter(RSSItem.source.in_(source_list))

        # Apply search term filtering if a search term is provided
        if search_term:
            try:
                # If search term is a date
                date_obj = datetime.strptime(search_term, "%B %d, %Y")
                query = query.filter(func.date(RSSItem.pubDate) == date_obj.date())
            except ValueError:
                # If search term is not a date
                query = query.filter(RSSItem.title.ilike(f'%{search_term}%'))

        # Pagination and ordering
        items = query.order_by(desc(RSSItem.pubDate)).offset(offset).limit(limit).all()

        # Handle case when no items are found
        if not items and offset == 0:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)
        return items
    except Exception as e:
        logging.error(f"Error in search items: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)

@router.get("/info/session/{chamber}")
async def get_congress_session_info(chamber: str, db: AsyncSession = Depends(get_db)):
    """
    Get next meeting information for a specific congressional chamber.
    """
    try:
        if chamber == CHAMBER_SENATE:
            result = db.query(SenateInfo).first()
        elif chamber == CHAMBER_HOUSE:
            result = db.query(HouseInfo).first()
        else:
            raise HTTPException(status_code=400, detail=INVALID_CHAMBER_DETAIL)

        if result is None:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)

        return {
            "in_session": result.in_session,
            "next_meeting": result.next_meeting,
            "live_link": result.live_link,
            "last_updated": result.last_updated,
        }
    except Exception as e:
        logging.error(f"Error fetching congress session info for {chamber}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)