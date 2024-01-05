from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import Base, engine
from app.api import router as api_router
from app.rss_fetcher import fetch_and_store_rss, fetch_session_info

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://congress.cipherkeeper.dev", "*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Accept"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(api_router)

# Check for new data
fetch_and_store_rss();
fetch_session_info("senateppg-twitter");
fetch_session_info("housedailypress-twitter");

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Schedule the task
scheduler.add_job(fetch_and_store_rss, "interval", minutes=2)
scheduler.add_job(fetch_session_info, "interval", minutes=15, args=["senateppg-twitter"])
scheduler.add_job(fetch_session_info, "interval", minutes=15, args=["housedailypress-twitter"])
scheduler.start()
