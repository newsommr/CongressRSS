from app.database import Base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
import datetime

class RSSItem(Base):
    __tablename__ = "rss_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    link = Column(String, unique=True)
    pubDate = Column(DateTime, index=True)
    source = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

class CongressInfo(Base):
    __tablename__ = "congress_info"
    id = Column(Integer, primary_key=True)
    senate_next_meeting = Column(String, default="")
    house_next_meeting = Column(String, default="")
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)