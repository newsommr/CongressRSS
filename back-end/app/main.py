from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import Base, engine
from app.api import router as api_router
from app.rss_fetcher import (
    fetch_and_store_rss,
    fetch_session_info,
    fetch_president_schedule,
)
import logging


app = FastAPI()

# CORS Middleware
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

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Check for new data
fetch_and_store_rss()
fetch_session_info()
fetch_president_schedule()


@app.on_event("startup")
async def schedule_fetching():
    scheduler.add_job(fetch_and_store_rss, "interval", minutes=2)
    scheduler.add_job(fetch_session_info, "interval", minutes=15)
    scheduler.add_job(fetch_president_schedule, "interval", minutes=15)
    scheduler.start()
