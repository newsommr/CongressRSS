from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.rss_fetcher import fetch_rss_data
from app.database import create_rss_item, get_db, Base, engine
from app.api import router as api_router

# Initialize FastAPI app
app = FastAPI()

origins = [
    "https://congress.cipherkeeper.dev",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Define task for fetching RSS data
def fetch_and_store_rss():
    print("running")
    db = next(get_db())
    for url, source in [("https://rules.house.gov/rss.xml", "house-rules-committee"), 
                        ("https://www.whitehouse.gov/briefing-room/legislation/feed/", "white-house-legislation"),
                        ("https://www.whitehouse.gov/briefing-room/presidential-actions/feed/rss", "white-house-presidential-actions"),
                        ("https://nitter.x86-64-unknown-linux-gnu.zip/SenatePPG/rss", "senateppg-twitter"),
                        ("https://nitter.x86-64-unknown-linux-gnu.zip/HouseDailyPress/rss", "housedailypress-twitter"),
                        ("https://rssproxy.migor.org/api/w2f?v=0.1&url=https%3A%2F%2Fwww.justice.gov%2Folc%2Fopinions&link=.%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fh2%5B1%5D%2Fa%5B1%5D&context=%2F%2Fdiv%5B3%5D%2Fmain%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B3%5D%2Fdiv%5B1%5D%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B2%5D%2Fdiv%5B4%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv&date=.%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B1%5D%2Ftime%5B1%5D&re=none&out=atom", "doj-olc-opinions")]:
        items = fetch_rss_data(url, source)  # Include the source here
        for item in items:
            create_rss_item(db, item)


# Schedule the task
scheduler.add_job(fetch_and_store_rss, "interval", minutes=5)
scheduler.start()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(api_router)

# Check for new data
fetch_and_store_rss();
