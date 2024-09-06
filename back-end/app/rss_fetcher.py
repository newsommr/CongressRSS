import re
from datetime import datetime, timezone, timedelta
import feedparser
from sqlalchemy import desc
from sqlalchemy.orm import Session
import logging
import pytz

from app.contact_llm import send_prompt
from app.models import FeedItem, SessionInfo, PresidentSchedule
from app.crud import (
    get_db,
    update_meeting_info,
    add_feed_item,
    update_president_schedule,
)
from app.utils import RSS_FEEDS, fetch

# Constants for file paths
SENATE_PROMPT_FILE = "app/prompts/senate_prompt.txt"
HOUSE_PROMPT_FILE = "app/prompts/house_prompt.txt"

SENATE_SOURCE = "senateppg-twitter"
HOUSE_SOURCE = "housedailypress-twitter"


def fetch_and_store_rss():
    """
    Fetches RSS feed data and stores it in the database.
    """
    db = next(get_db())
    for rss_url, source in RSS_FEEDS:
        try:
            parsed_data = feedparser.parse(rss_url)
            formatted_entries = format_entries(parsed_data.entries, source)
            add_feed_item(db, formatted_entries)
            db.commit()
        except Exception as e:
            logging.error(f"An error occurred in fetching RSS data from {rss_url}: {e}")
            db.rollback()
        finally:
            db.close()

def format_entries(parsed_data, source):
    """
    Formats the entries in an RSS feed.
    """
    valid_items = [entry for entry in parsed_data if all(attr in entry for attr in ["title", "link", "published_parsed"])]

    formatted_entries = []
    for entry in valid_items:
        if "nitter" in entry['link']:
            entry = handle_twitter_urls(entry)
            if entry is None:
                continue
        
        formatted_entries.append({
            "title": entry['title'],
            "link": entry['link'],
            "pubDate": datetime(*entry['published_parsed'][:6]),
            "source": source,
        })
    
    return formatted_entries

def handle_twitter_urls(entry):
    """
    Handles the addition of Twitter items.
    """
    # If the entry is a retweet (contains "RT by"), return None
    if "RT by" in entry['title']:
        return None

    # Remove 'R to @username: ' from the title if present
    entry['title'] = re.sub(r"^R to @\w+: ", "", entry['title'])

    # Modify the link to replace 'nitter' domain with 'twitter.com'
    entry['link'] = re.sub(r"https?://nitter\.[^/]+", "https://twitter.com", entry['link'])

    return entry


def fetch_president_schedule():
    db = next(get_db())
    #db.query(PresidentSchedule).delete()
    #db.commit()
    response = fetch("https://media-cdn.factba.se/rss/json/calendar-full.json")
    if not response:
        return
    try:
        items = response.json()
        for item in items:
            # Use the 'date' field with 12:00 AM if 'time' is missing or null
            time_str = item.get("time") if item.get("time") is not None else "00:00:00"

            date_time_str = f"{item['date']} {time_str}"
            try:
                date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
                year, month, day, hour, minute = (
                    date_time_obj.year,
                    date_time_obj.month,
                    date_time_obj.day,
                    date_time_obj.hour,
                    date_time_obj.minute,
                )
                utc_time_obj = convert_to_utc(
                    year, month, day, hour, minute, timezone="US/Eastern"
                )
            except ValueError as ve:
                logging.error(f"Date parsing error for item {item}: {ve}")
                continue

            parsed_item = {
                "link": item.get("url", None),
                "location": item.get("location", ""),
                "time": utc_time_obj,
                "description": item.get("details", ""),
                "press_information": item.get("coverage", ""),
            }
            update_president_schedule(db, parsed_item)
        db.commit()
    except Exception as e:
        logging.error(
            f"An error occurred in fetching and updating the President's schedule: {e}"
        )
        db.rollback()
    finally:
        db.close()


def fetch_session_info():
    """
    Fetches session information from the database and sends a prompt to the LLM.
    """
    db = next(get_db())

    house_info = get_house_floor_info(db)
    if house_info is not None:
        in_session, next_meeting, live_link = house_info
        update_meeting_info(db, "house", in_session, next_meeting, live_link)

    senate_info = get_senate_floor_info()
    if senate_info is not None:
        in_session, next_meeting, live_link = senate_info
        update_meeting_info(db, "senate", in_session, next_meeting, live_link)
    
    try:
        db.commit()
    except Exception as e:
        logging.error(f"Couldn't update session information into the db: {e}")
        db.rollback()
    finally:
        db.close()


def get_house_floor_info(db):
    response = fetch("https://in-session.house.gov/")
    if not response:
        return

    try:
        live_link = "https://live.house.gov"
        in_session = int(response.text)
        
        items = (
            db.query(FeedItem)
            .filter(FeedItem.source == HOUSE_SOURCE)
            .filter(FeedItem.title.ilike('%adjourned%'))
            .order_by(desc(FeedItem.pubDate))
            .limit(15)
            .all()
        )
        items_str = "\n".join(
            [f"Title: {item.title}, Date: {item.pubDate}" for item in items]
        )
        current_date = datetime.now().strftime("%B %d, %Y")
        prompt_template = get_prompt_template(HOUSE_SOURCE)
        prompt = prompt_template.format(current_date=current_date) + "\n\n" + items_str

        next_meeting_date_str = send_prompt(prompt)
        next_meeting_date = datetime.fromisoformat(next_meeting_date_str)

        next_meeting_date_utc = convert_to_utc(
            next_meeting_date.year, 
            next_meeting_date.month, 
            next_meeting_date.day, 
            next_meeting_date.hour, 
            next_meeting_date.minute
        )
        
        return in_session, next_meeting_date_utc, live_link

    except (ValueError, KeyError, TypeError) as e:
        logging.error(f"Couldn't get House session information: {e}")
        return None


def get_senate_floor_info():
    response = fetch("https://www.senate.gov/legislative/schedule/floor_schedule.json")
    if not response:
        return

    try:
        data = response.json()
        proceedings = data.get("floorProceedings", [])
        current_date_time_utc = datetime.now(timezone.utc)

        for item in proceedings:
            convene_date_time_utc = convert_to_utc(
                    int(item["conveneYear"]),
                    int(item["conveneMonth"]),
                    int(item["conveneDay"]),
                    int(item["conveneHour"]),
                    int(item["conveneMinutes"]),
                )

            in_session = int(current_date_time_utc >= convene_date_time_utc)
            live_link = item["convenedSessionStream"]

            return in_session, convene_date_time_utc, live_link
    except ValueError as e:
        logging.error(f"Error parsing JSON for Senate's floor schedule: {e}")


def convert_to_utc(year, month, day, hour, minute, timezone="America/New_York"):
    """
    Convert a given date and time from a specified timezone to UTC.
    """
    local = pytz.timezone(timezone)
    local_dt = local.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def get_prompt_template(source: str) -> str:
    """
    Retrieves the appropriate prompt template based on the source.
    """
    filename = (
        SENATE_PROMPT_FILE if source == "senateppg-twitter" else HOUSE_PROMPT_FILE
    )
    with open(filename, "r") as file:
        return file.read()
