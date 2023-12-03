from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///rssfeed.db")
SessionLocal = sessionmaker(bind=engine)

class Rules(Base):
    __tablename__ = "rules_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)
    pubDate = Column(DateTime)
    hash = Column(String, unique=True)


class SignedLegislation(Base):
    __tablename__ = "signed_legislation_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)
    pubDate = Column(DateTime)
    hash = Column(String, unique=True)
