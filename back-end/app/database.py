from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import datetime

DATABASE_URL = "sqlite:///./congressrss.db"  # SQLite database URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RSSItem(Base):
    __tablename__ = "rss_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    link = Column(String, unique=True)
    pubDate = Column(DateTime, index=True)
    source = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_rss_item(db: Session, rss_item):
    # Check if an item with the same title and link already exists
    existing_item = db.query(RSSItem).filter(RSSItem.title == rss_item['title'], RSSItem.link == rss_item['link']).first()
    if existing_item is not None:
        # Item already exists, so don't add it again
        return existing_item

    # Create a new RSSItem object
    db_item = RSSItem(
        title=rss_item['title'],
        link=rss_item['link'],
        pubDate=rss_item['pubDate'],
        source=rss_item['source'],
        fetched_at=datetime.datetime.utcnow()
    )

    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        # Handle the case where the item was added by another process/thread in the meantime
        return db.query(RSSItem).filter(RSSItem.title == rss_item['title'], RSSItem.link == rss_item['link']).first()

