from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from time_util import current_time

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=current_time(), onupdate=current_time())
    updated_at = Column(DateTime(timezone=True), default=current_time(), onupdate=current_time())

class FeedItem(Base, TimestampMixin):
    __tablename__ = "feed_items"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    link = Column(String)
    pubDate = Column(DateTime(timezone=True), index=True)
    source = Column(String)
class SessionInfo(Base, TimestampMixin):
    __tablename__ = "session_info"
    id = Column(Integer, primary_key=True)
    chamber = Column(String)
    meeting_date = Column(DateTime(timezone=True))
    in_session = Column(Integer)
    live_link = Column(String)
class PresidentSchedule(Base, TimestampMixin):
    __tablename__ = 'president_schedule'
    id = Column(Integer, primary_key=True)
    link = Column(String)
    location = Column(String)
    time = Column(DateTime(timezone=True), index=True)
    description = Column(String, index=True)
    press_information = Column(String)
