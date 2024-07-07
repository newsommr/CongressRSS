from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from app.models import SessionInfo, FeedItem, PresidentSchedule
from app.database import SessionLocal
from datetime import datetime
import pytz
from app.time_util import current_time

# Constants
SENATE_SOURCE = "senateppg-twitter"
HOUSE_SOURCE = "housedailypress-twitter"


def get_db():
    with SessionLocal() as db:
        yield db


def add_feed_item(db: Session, feed_item: dict):

    title, pubDate, link = feed_item["title"], feed_item["pubDate"], feed_item["link"]
    existing_item = (
        db.query(FeedItem).filter_by(title=title, pubDate=pubDate, link=link).first()
    )
    if existing_item:
        return
    new_item = FeedItem(**feed_item)
    db.add(new_item)


def update_meeting_info(
    db: Session, chamber: str, in_session: int, next_meeting=None, live_link: str = None
):

    session_info = db.query(SessionInfo).filter_by(chamber=chamber).delete()
    new_item = SessionInfo(
        chamber=chamber,
        meeting_date=next_meeting,
        in_session=in_session,
        live_link=live_link,
    )
    db.add(new_item)


def update_president_schedule(db: Session, president_schedule: dict):
    time, location, description = (
        president_schedule["time"],
        president_schedule["location"],
        president_schedule["description"],
    )
    existing_item = (
        db.query(PresidentSchedule)
        .filter_by(time=time, location=location, description=description)
        .first()
    )
    if existing_item:
        return

    new_item = PresidentSchedule(**president_schedule)
    db.add(new_item)
