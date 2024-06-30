from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, or_
from sqlalchemy.exc import SQLAlchemyError
from app.models import RSSItem, SenateInfo, HouseInfo, PresidentSchedule
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
    Search RSS items by term, with optional source filtering.
    """
    validate_pagination(limit, offset)

    try:
        rss_query = db.query(RSSItem)
        president_schedule_query = db.query(PresidentSchedule)
        potus_schedule_included = True

        # Apply source filtering if sources are provided
        if sources:
            source_list = sources.split(',')
            rss_query = rss_query.filter(RSSItem.source.in_(source_list))
            potus_schedule_included = 'potus-schedule' in source_list

        # Apply search term filtering if a search term is provided
        if search_term:
            date_filter_applied = False
            try:
                # If search term is a date
                date_obj = datetime.strptime(search_term, "%B %d, %Y")
                rss_query = rss_query.filter(func.date(RSSItem.pubDate) == date_obj.date())
                president_schedule_query = president_schedule_query.filter(func.date(PresidentSchedule.time) == date_obj.date())
                date_filter_applied = True
            except ValueError:
                # If search term is not a date, apply text search
                rss_query = rss_query.filter(RSSItem.title.ilike(f'%{search_term}%'))
                if not date_filter_applied:
                    president_schedule_query = president_schedule_query.filter(
                        or_(
                            PresidentSchedule.description.ilike(f'%{search_term}%'),
                            PresidentSchedule.location.ilike(f'%{search_term}%')
                        )
                    )

        # Fetch RSS items and POTUS schedule items without pagination
        rss_items = rss_query.order_by(desc(RSSItem.pubDate)).all()
        president_schedule_items = []
        if potus_schedule_included:
            president_schedule_items = president_schedule_query.all()
            president_schedule_items = [format_president_schedule_item(item) for item in president_schedule_items]

        # Combine, sort, and then apply pagination to the combined list
        combined_items = sorted(rss_items + president_schedule_items, key=get_pub_date, reverse=True)
        paginated_combined_items = combined_items[offset:offset + limit]

        # Handle case when no items are found
        if not paginated_combined_items and offset == 0:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)

        return paginated_combined_items
    except Exception as e:
        logging.error(f"Error in search items: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


def get_pub_date(item):
    if isinstance(item, RSSItem):
        return item.pubDate
    elif isinstance(item, dict):
        return item['pubDate']
    else:
        return None  # or some default date

def format_president_schedule_item(item):
    """
    Format PresidentSchedule item to match RSS item structure.
    """
    # Construct a title based on PresidentSchedule's data. Include location only if it's not None
    if item.location:
        title = f"{item.description} ({item.location})"
    else:
        title = item.description

    # Format item as RSSItem-like dictionary
    formatted_item = {
        'title': title,
        'link': item.link,
        'pubDate': item.time,
        'source': 'potus-schedule'
    }
    return formatted_item



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

@router.get("/info/president-schedule/")
async def get_president_session_info(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Returns the President's public schedule, with optional source filtering and pagination.
    """
    validate_pagination(limit, offset)
    try:
        query = db.query(PresidentSchedule).order_by(desc(PresidentSchedule.time)).offset(offset).limit(limit)

        # Execute the query
        result = query.all()

        if result is None:
            raise HTTPException(status_code=404, detail=ITEMS_NOT_FOUND_DETAIL)

        return result
    except Exception as e:
        logging.error(f"Error fetching the President's Schedule: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)

def format_response(status, data, message):
    return {
        "status": status,
        "data": data,
        "message": message
    }
