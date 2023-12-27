from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from app.models import RSSItem, CongressInfo
from app.database import SessionLocal
from datetime import datetime

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
        return existing_item

    new_item = RSSItem(**rss_item, fetched_at=datetime.utcnow())
    db.add(new_item)
    try:
        db.commit()
        return new_item
    except IntegrityError as e:
        logging.error(f"An error occurred in adding an item to the database: {new_item}: {e}")
        db.rollback()
        return db.query(RSSItem).filter_by(title=title, link=link).first()

def update_meeting_info(db: Session, source: str, next_meeting_date: str):
    """
    Updates or adds the meeting information in the database.
    """
    congress_info = db.query(CongressInfo).first()
    if congress_info:
        update_congress_info(congress_info, source, next_meeting_date)
    else:
        congress_info = create_congress_info(source, next_meeting_date)
        db.add(congress_info)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"An error occurred in updating the upcoming meeting information for Congress: {next_meeting_date}: {e}")

def update_congress_info(congress_info, source: str, next_meeting_date: str):
    """
    Updates existing CongressInfo record.
    """
    if source == SENATE_SOURCE:
        congress_info.senate_next_meeting = next_meeting_date
    elif source == HOUSE_SOURCE:
        congress_info.house_next_meeting = next_meeting_date
    congress_info.last_updated = datetime.utcnow()

def create_congress_info(source: str, next_meeting_date: str) -> CongressInfo:
    """
    Creates a new CongressInfo record.
    """
    if source == SENATE_SOURCE:
        return CongressInfo(senate_next_meeting=next_meeting_date, last_updated=datetime.utcnow())
    elif source == HOUSE_SOURCE:
        return CongressInfo(house_next_meeting=next_meeting_date, last_updated=datetime.utcnow())
