from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from app.models import RSSItem, HouseInfo, SenateInfo
from app.database import SessionLocal
from datetime import datetime
import pytz

# Constants
SENATE_SOURCE = "senateppg-twitter"
HOUSE_SOURCE = "housedailypress-twitter"

def get_db():
    """
    Safely yields the database session.
    """
    with SessionLocal() as db:
        yield db

# Function to create RSS item
def create_rss_item(db: Session, rss_item: dict) -> RSSItem:
    """
    Adds new rss_items to the database.
    """
    title, link = rss_item['title'], rss_item['link']
    existing_item = db.query(RSSItem).filter_by(title=title, link=link).first()
    if existing_item:
        return

    new_item = RSSItem(**rss_item, fetched_at=datetime.utcnow())
    db.add(new_item)

def update_meeting_info(db: Session, source: str, in_session: int, next_meeting = None, live_link: str = None):
    """
    Updates or adds the meeting information in the database.
    """

    if source == SENATE_SOURCE:
        senate_info = db.query(SenateInfo).first()

        if senate_info:
            update_senate_info(senate_info, in_session, next_meeting, live_link)
        else:
            senate_info = create_senate_info(in_session, next_meeting, live_link)
            db.add(senate_info)

    elif source == HOUSE_SOURCE:
        house_info = db.query(HouseInfo).first()

        if house_info:
            update_house_info(house_info, in_session, next_meeting, live_link)
        else:
            house_info = create_house_info(in_session, next_meeting, live_link)
            db.add(house_info)

def update_senate_info(senate_info, in_session: int, next_meeting, live_link):
    """
    Updates existing SenateInfo record.
    """
    senate_info.in_session = in_session
    senate_info.next_meeting = next_meeting
    senate_info.live_link = live_link
    senate_info.last_updated = datetime.now(pytz.utc)


def update_house_info(house_info, in_session: int, next_meeting, live_link):
    """
    Updates existing HouseInfo record.
    """
    house_info.in_session = in_session
    house_info.next_meeting = next_meeting
    house_info.live_link = live_link
    house_info.last_updated = datetime.now(pytz.utc)
    
def create_senate_info(in_session: int, next_meeting, live_link) -> SenateInfo:
    """
    Creates a new SenateInfo record.
    """
    return SenateInfo(in_session=in_session, next_meeting=next_meeting, live_link=live_link, last_updated=datetime.now(pytz.utc))

def create_house_info(in_session: int, next_meeting, live_link) -> HouseInfo:
    """
    Creates a new HouseInfo record.
    """
    return HouseInfo(in_session=in_session, next_meeting=next_meeting, live_link=live_link, last_updated=datetime.now(pytz.utc))
