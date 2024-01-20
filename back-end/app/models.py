from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime
import pytz

class RSSItem(Base):
    __tablename__ = "rss_items"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    link = Column(String, default=None)
    pubDate = Column(DateTime(timezone=True), index=True)
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
    __tablename__ = 'president_schedule'
    id = Column(Integer, primary_key=True)
    link = Column(String, default=None)
    location = Column(String, default="")
    time = Column(DateTime(timezone=True), default=None, index=True)
    description = Column(String, default="", index=True)
    press_information = Column(String, default="")
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))
