import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import Rules, SignedLegislation, Base, engine, SessionLocal
from app.rss_fetcher import fetch_rss_data
from sqlalchemy import Column, Integer, String, DateTime, exists


app = FastAPI()

origins = [
    "https:congress.cipherkeeper.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Rules.metadata.create_all(engine)
SignedLegislation.metadata.create_all(engine)

@app.on_event("startup")
async def startup_event():
    session = SessionLocal()
    try:
        rules_data = fetch_rss_data('https://rules.house.gov/rss.xml')
        legislation_data = fetch_rss_data('https://www.whitehouse.gov/briefing-room/legislation/feed/')

        # Sort data by 'pubDate' (assuming it's in a suitable format for sorting)
        sorted_rules_data = sorted(rules_data, key=lambda x: x['pubDate'])
        sorted_legislation_data = sorted(legislation_data, key=lambda x: x['pubDate'])

        for item_data in sorted_rules_data:
            item_hash = hashlib.md5(f"{item_data['title']}{item_data['link']}{item_data['pubDate']}".encode()).hexdigest()
            if not session.query(exists().where(Rules.hash == item_hash)).scalar():
                item = Rules(**item_data, hash=item_hash)
                session.add(item)

        for item_data in sorted_legislation_data:
            item_hash = hashlib.md5(f"{item_data['title']}{item_data['link']}{item_data['pubDate']}".encode()).hexdigest()
            if not session.query(exists().where(SignedLegislation.hash == item_hash)).scalar():
                item = SignedLegislation(**item_data, hash=item_hash)
                session.add(item)

        session.commit()
    finally:
        session.close()

@app.get("/rules")
async def get_rules():
    session = SessionLocal()
    try:
        items = session.query(Rules).all()
        return items
    finally:
        session.close()

@app.get("/signed_legislation")
async def get_signed_legislation():
    session = SessionLocal()
    try:
        items = session.query(SignedLegislation).all()
        return items
    finally:
        session.close()
