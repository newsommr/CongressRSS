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


app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://congress.cipherkeeper.dev"],
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

fetch_president_schedule()
fetch_session_info()
fetch_and_store_rss()

@app.on_event("startup")
async def schedule_fetching():
    scheduler.add_job(fetch_and_store_rss, "interval", minutes=5, misfire_grace_time=60, max_instances=3)
    scheduler.add_job(fetch_session_info, "interval", minutes=30, misfire_grace_time=60, max_instances=3)
    scheduler.add_job(fetch_president_schedule, "interval", minutes=30, misfire_grace_time=60, max_instances=3)
    scheduler.start()
