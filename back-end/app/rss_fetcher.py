import re
from datetime import datetime, timezone
import feedparser
from sqlalchemy import desc
from sqlalchemy.orm import Session
import logging
import pytz
import requests

from app.contact_llm import send_prompt
from app.models import RSSItem, HouseInfo, SenateInfo
from app.crud import get_db, update_meeting_info, create_rss_item

# Constants for file paths
SENATE_PROMPT_FILE = 'app/prompts/senate_prompt.txt'
HOUSE_PROMPT_FILE = 'app/prompts/house_prompt.txt'

SENATE_SOURCE = "senateppg-twitter"
HOUSE_SOURCE = "housedailypress-twitter"

def fetch_and_store_rss():
    """
    Fetches RSS feed data from multiple sources and stores it in the database.
    """
    db = next(get_db())
    rss_feeds = [
                    ("https://rules.house.gov/rss.xml", "house-rules-committee"), 
                    ("https://www.whitehouse.gov/briefing-room/legislation/feed/", "white-house-legislation"),
                    ("https://www.whitehouse.gov/briefing-room/presidential-actions/feed/rss", "white-house-presidential-actions"),
                    ("https://nitter.x86-64-unknown-linux-gnu.zip/SenatePPG/rss", "senateppg-twitter"),
                    ("https://nitter.x86-64-unknown-linux-gnu.zip/HouseDailyPress/rss", "housedailypress-twitter"),
                    ("https://rssproxy.migor.org/api/w2f?v=0.1&url=https%3A%2F%2Fwww.justice.gov%2Folc%2Fopinions&link=.%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fh2%5B1%5D%2Fa%5B1%5D&context=%2F%2Fdiv%5B3%5D%2Fmain%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B3%5D%2Fdiv%5B1%5D%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B2%5D%2Fdiv%5B4%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv&date=.%2Farticle%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B1%5D%2Ftime%5B1%5D&re=none&out=atom", "doj-olc-opinions"),
                    ("https://rssproxy.migor.org/api/w2f?v=0.1&url=https%3A%2F%2Fwww.gao.gov%2Freports-testimonies&link=.%2Fdiv%5B1%5D%2Fspan%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fh4%5B1%5D%2Fa%5B1%5D&context=%2F%2Fdiv%5B1%5D%2Fdiv%5B3%5D%2Fdiv%5B4%5D%2Fmain%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B2%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fsection%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv&date=.%2Fdiv%5B1%5D%2Fspan%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fdiv%5B1%5D%2Fspan%5B1%5D%2Ftime%5B1%5D&re=none&out=atom", "gao-reports"),
                    ("https://www.dsca.mil/press-media/major-arms-sales/feed", "dsca-major-arms-sales"),
                ]

    for rss_url, source in rss_feeds:
        try:
            parsed_data = feedparser.parse(rss_url)
            entries = [entry for entry in parsed_data.entries if is_valid_entry(entry)]

            for entry in entries:
                item = parse_entry(entry, source)
                if item is not None:
                    create_rss_item(db, item)

            db.commit()
        except Exception as e:
            logging.error(f"An error occurred in fetching RSS data from {rss_url}: {e}")
            db.rollback()
        finally:
            db.close()

def is_valid_entry(entry) -> bool:
    """
    Checks if the entry has the required attributes.
    """
    return all(hasattr(entry, attr) for attr in ['title', 'link', 'published_parsed'])

def parse_entry(entry, source: str) -> dict:
    """
    Parses an entry from the RSS feed.
    """
    if 'nitter' in entry.link:
        entry = handle_twitter_urls(entry)
        if not entry:
            return None

    return {
        "title": entry.title,
        "link": entry.link,
        "pubDate": datetime(*entry.published_parsed[:6]),
        "source": source
    }

def handle_twitter_urls(entry):
    """
    Handles the modification of Twitter URLs in the feed entry. Returns None for retweets.
    """
    # If the entry is a retweet (contains "RT by"), return None
    if "RT by" in entry.title:
        return None

    # Remove 'R to @username: ' from the title if present
    entry.title = re.sub(r'^R to @\w+: ', '', entry.title)

    # Modify the link to replace 'nitter' domain with 'twitter.com'
    entry.link = re.sub(r'https?://nitter\.[^/]+', 'https://twitter.com', entry.link)

    return entry



def fetch_session_info(source: str):
    """
    Fetches session information from the database and sends a prompt to the LLM.
    """
    db = next(get_db())

    try:
        if source == SENATE_SOURCE:
            in_session, next_meeting, live_link = get_senate_floor_info()
            update_meeting_info(db, source, in_session, next_meeting, live_link)
        if source == HOUSE_SOURCE:
            in_session, next_meeting = get_house_floor_info(db)
            update_meeting_info(db, source, in_session, next_meeting)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"An error occurred in updating the upcoming meeting information for Congress: {e}")
    finally:
        db.close()

def get_house_floor_info(db):
    try:
        response = requests.get("https://in-session.house.gov/")
        in_session = int(response.text)
        items = db.query(RSSItem)\
             .filter(RSSItem.source == HOUSE_SOURCE)\
             .order_by(desc(RSSItem.pubDate))\
             .limit(15)\
             .all()
        items_str = "\n".join([f"Title: {item.title}, Date: {item.pubDate}" for item in items])
        current_date = datetime.now().strftime("%B %d, %Y")
        prompt_template = get_prompt_template(HOUSE_SOURCE)
        prompt = prompt_template.format(current_date=current_date) + "\n\n" + items_str

        next_meeting_date_str = send_prompt(prompt)
        next_meeting_date = datetime.fromisoformat(next_meeting_date_str)

        year = next_meeting_date.year
        month = next_meeting_date.month
        day = next_meeting_date.day
        hour = next_meeting_date.hour
        minute = next_meeting_date.minute

        # Convert to UTC using your function
        next_meeting_date_utc = convert_to_utc(year, month, day, hour, minute)
        return in_session, next_meeting_date_utc
    except ValueError as e:
        logging.error(f"Couldn't parse string as an int: {response} - {e}")
    except Exception as e:
        logging.error(f"Couldn't get House session information: {response} - {e}")

def get_senate_floor_info():
    try:
        response = requests.get("https://www.senate.gov/legislative/schedule/floor_schedule.json")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving the Senate floor schedule: {e}")
        return

    data = response.json()
    proceedings = data.get('floorProceedings', [])
    current_date_time_utc = datetime.now(timezone.utc)

    for item in proceedings:
        try:
            convene_date_time_utc = convert_to_utc(
                int(item['conveneYear']),
                int(item['conveneMonth']),
                int(item['conveneDay']),
                int(item['conveneHour']),
                int(item['conveneMinutes'])
            )

            if current_date_time_utc >= convene_date_time_utc:
                in_session = 1
            else:
                in_session = 0
            live_link = item['convenedSessionStream']
        except Exception as e:
            logging.warning(f"Error processing item in proceedings: {item} - {e}")

    return in_session, convene_date_time_utc, live_link

def convert_to_utc(year, month, day, hour, minute, timezone='America/New_York'):
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
    filename = SENATE_PROMPT_FILE if source == "senateppg-twitter" else HOUSE_PROMPT_FILE
    with open(filename, 'r') as file:
        return file.read()
