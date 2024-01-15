from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime
import pytz

class RSSItem(Base):
    __tablename__ = "rss_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    link = Column(String, unique=True)
    pubDate = Column(DateTime, index=True)
    source = Column(String)
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))
class HouseInfo(Base):
    __tablename__ = "house_info"
    id = Column(Integer, primary_key=True)
    next_meeting = Column(DateTime(timezone=True), default=None)
    in_session = Column(Integer, default=0)
    live_link = Column(String, default="")
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))
class SenateInfo(Base):
    __tablename__ = "senate_info"
    id = Column(Integer, primary_key=True)
    next_meeting = Column(DateTime(timezone=True), default=None)
    in_session = Column(Integer, default=0)
    live_link = Column(String, default="")
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))
class PresidentSchedule(Base):
    __tablename__ = 'president_schedulee'
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, default="")
    time = Column(DateTime(timezone=True), default=None)
    description = Column(String, default="")
    press_information = Column(String, default="")
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))