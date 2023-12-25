from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models import RSSItem, CongressInfo
from app.database import SessionLocal
from datetime import datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_rss_item(db: Session, rss_item: dict) -> RSSItem:
    existing_item = db.query(RSSItem).filter_by(title=rss_item['title'], link=rss_item['link']).first()
    if existing_item:
        return existing_item

    new_item = RSSItem(**rss_item, fetched_at=datetime.datetime.utcnow())
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except IntegrityError:
        db.rollback()
        return db.query(RSSItem).filter_by(title=rss_item['title'], link=rss_item['link']).first()

def update_meeting_info(db: Session, source: str, next_meeting_date: str):
    """
    Updates the meeting information in the database.
    """
    congress_info = db.query(CongressInfo).first()
    if congress_info:
        update_congress_info(congress_info, source, next_meeting_date)
    else:
        add_new_congress_info(db, source, next_meeting_date)
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()


def update_congress_info(congress_info, source: str, next_meeting_date: str):
    """
    Updates existing CongressInfo record.
    """
    if source == "senateppg-twitter":
        congress_info.senate_next_meeting = next_meeting_date
    elif source == "housedailypress-twitter":
        congress_info.house_next_meeting = next_meeting_date
    congress_info.last_updated = datetime.utcnow()


def add_new_congress_info(db: Session, source: str, next_meeting_date: str):
    """
    Adds a new CongressInfo record to the database.
    """
    if source == "senateppg-twitter":
        congress_info = CongressInfo(senate_next_meeting=next_meeting_date)
    elif source == "housedailypress-twitter":
        congress_info = CongressInfo(house_next_meeting=next_meeting_date)
    db.add(congress_info)