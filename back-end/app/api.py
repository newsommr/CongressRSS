from app.models import RSSItem, SenateInfo, HouseInfo, PresidentSchedule
from app.crud import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy import desc, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
import re

INVALID_BOUNDS = "Invalid limit/offset value. Must be > 0"
ITEMS_NOT_FOUND = "Items not found"
INTERNAL_SERVER_ERROR = "Internal server error"
DATE_DOES_NOT_EXIST = (
    "The supplied date format was correct, but the date is not possible."
)

router = APIRouter()


@router.get("/feed")
async def retrieve_feed(
    search_term: str = "",
    sources: str = "",
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Search entire feed, with optional filtering by sources, specific keywords, or dates.
    """
    status = "error"
    data = None
    message = None
    if is_valid_bounds(limit, offset):
        rss_query = db.query(RSSItem)
        president_schedule_query = db.query(PresidentSchedule)
        potus_schedule_included = True

        # Apply source filtering if sources are provided
        if sources:
            source_list = sources.split(",")
            rss_query = rss_query.filter(RSSItem.source.in_(source_list))
            potus_schedule_included = "potus-schedule" in source_list

        # Apply search term filtering if a search term is provided
        if search_term:
            # If the input matches the date format, search for items with that date.
            if is_valid_date(search_term):
                try:
                    date_obj = datetime.strptime(search_term, "%B %d, %Y")
                    rss_query = rss_query.filter(
                        func.date(RSSItem.pubDate) == date_obj.date()
                    )
                    president_schedule_query = president_schedule_query.filter(
                        func.date(PresidentSchedule.time) == date_obj.date()
                    )
                except ValueError:
                    return formatted_response(status, data, DATE_DOES_NOT_EXIST)
            else:
                # If search term is not a date, apply text search
                rss_query = rss_query.filter(RSSItem.title.ilike(f"%{search_term}%"))
                president_schedule_query = president_schedule_query.filter(
                    or_(
                        PresidentSchedule.description.ilike(f"%{search_term}%"),
                        PresidentSchedule.location.ilike(f"%{search_term}%"),
                    )
                )

        # Fetch RSS items and POTUS schedule items with pagination
        rss_items = (
            rss_query.order_by(desc(RSSItem.pubDate)).offset(offset).limit(limit).all()
        )
        rss_items = [
            {
                "title": item.title,
                "link": item.link,
                "pubDate": item.pubDate,
                "source": item.source,
                "fetched_at": item.fetched_at,
            }
            for item in rss_items
        ]

        president_schedule_items = []
        if potus_schedule_included:
            president_schedule_items = (
                president_schedule_query.offset(offset).limit(limit).all()
            )
            president_schedule_items = [
                format_president_schedule_item(item)
                for item in president_schedule_items
            ]

        # Combine, sort, and then return the paginated results
        combined_items = sorted(
            rss_items + president_schedule_items, key=get_pub_date, reverse=True
        )
        paginated_combined_items = combined_items[:limit]

        if combined_items:
            status = "success"
            data = paginated_combined_items
        else:
            message = ITEMS_NOT_FOUND
    else:
        message = INVALID_BOUNDS
    return formatted_response(status, data, message)


def get_pub_date(item):
    if isinstance(item, RSSItem):
        return item.pubDate
    elif isinstance(item, dict):
        return item["pubDate"]
    else:
        return None


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
        "title": title,
        "link": item.link,
        "pubDate": item.time,
        "source": "potus-schedule",
    }
    return formatted_item


@router.get("/legislative/session-info")
async def get_congress_session_info(db: AsyncSession = Depends(get_db)):
    """
    Returns the next meeting information for the House/Senate.
    """
    status = "error"
    data = None
    message = None

    senate = db.query(SenateInfo).first()
    house = db.query(HouseInfo).first()

    if senate and house:
        status = "success"
        data = [
            {
                "chamber": "senate",
                "in_session": senate.in_session,
                "next_meeting": senate.next_meeting,
                "live_link": senate.live_link,
                "last_updated": senate.last_updated,
            },
            {
                "chamber": "house",
                "in_session": house.in_session,
                "next_meeting": house.next_meeting,
                "live_link": house.live_link,
                "last_updated": house.last_updated,
            },
        ]
    else:
        message = ITEMS_NOT_FOUND

    return formatted_response(status, data, message)


@router.get("/executive/potus-schedule/")
async def get_potus_schedule(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """
    Returns the President's public schedule, with optional source filtering and pagination.
    """
    status = "error"
    data = None
    message = None
    result = None
    if is_valid_bounds(limit, offset):
        result = (
            db.query(PresidentSchedule)
            .order_by(desc(PresidentSchedule.time))
            .offset(offset)
            .limit(limit)
            .all()
        )
    else:
        message = INVALID_BOUNDS

    if result:
        status = "success"
        data = [
            {
                "description": item.description,
                "link": item.link,
                "location": item.location,
                "time": item.time,
                "pubDate": item.time,
                "press_information": item.press_information,
                "last_updated": item.last_updated,
            }
            for item in result
        ]
    else:
        message = ITEMS_NOT_FOUND
    return formatted_response(status, data, message)


def formatted_response(status, data, message):
    return {"status": status, "data": data, "message": message}


def is_valid_bounds(limit, offset):
    """
    Validates the limit and offset for pagination
    """
    return limit > 0 and offset >= 0


def is_valid_date(search_term):
    pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}$"
    return re.match(pattern, search_term)
