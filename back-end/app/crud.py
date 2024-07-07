from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from app.models import FeedItem, SessionInfo, PresidentSchedule
from app.database import SessionLocal
from datetime import datetime
import pytz
from app.time_util import current_time

# Constants
SENATE_SOURCE = "senateppg-twitter"
HOUSE_SOURCE = "housedailypress-twitter"

def get_db():
    """
    Safely yields the database session.
    """
    with SessionLocal() as db:
        yield db

def create_rss_item(db: Session, rss_item: dict) -> FeedItem:
    """
    Adds new rss_items to the database.
    """
    
    title, pubDate = rss_item['title'], rss_item['pubDate']
    existing_item = db.query(FeedItem).filter_by(title=title, pubDate=pubDate).first()
    if existing_item:
        return
    new_item = FeedItem(**rss_item, modified_at=current_time())
    db.add(new_item)


def update_meeting_info(db: Session, chamber: str, in_session: int, next_meeting = None, live_link: str = None):
    """
    Updates or adds the meeting information in the database.
    """

    session_info = db.query(SessionInfo).filter_by(chamber=chamber).delete()
    new_item = SessionInfo(
        chamber = chamber,
        meeting_date = next_meeting,
        in_session = in_session,
        live_link = live_link,
        modified_at = current_time()
    )
    db.add(new_item)


def update_session_info(session_info, in_session: int, next_meeting, live_link):
    """
    Updates existing HouseInfo record.
    """
    house_info.in_session = in_session
    house_info.next_meeting = next_meeting
    house_info.live_link = live_link
    house_info.last_updated = datetime.now(pytz.utc)

def update_president_schedule(db: Session, president_schedule: dict) -> PresidentSchedule:
    """
    Adds new rss_items to the database.
    """
    link, location, time, description, press_information = president_schedule['link'], president_schedule['location'], president_schedule['time'], president_schedule['description'], president_schedule['press_information']
    existing_item = db.query(PresidentSchedule).filter_by(time=time, location=location, description=description).first()
    if existing_item:
        return

    new_item = PresidentSchedule(**president_schedule, modified_at=datetime.now(pytz.utc))
    db.add(new_item)