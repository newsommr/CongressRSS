import re
from datetime import datetime
import feedparser
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.contact_llm import send_prompt
from app.models import RSSItem, CongressInfo
from app.crud import get_db, update_meeting_info

# Constants for file paths
SENATE_PROMPT_FILE = 'app/prompts/senate_prompt.txt'
HOUSE_PROMPT_FILE = 'app/prompts/house_prompt.txt'


def fetch_rss_data(rss_url: str, source: str) -> list:
    """
    Fetches and parses the RSS feed data from a given URL.
    """
    try:
        parsed_data = feedparser.parse(rss_url)
        return [parse_entry(entry, source) for entry in parsed_data.entries if is_valid_entry(entry)]
    except feedparser.FeedParserError as e:
        logger.error(f"An error occurred in fetching RSS data: {e}")
        return []


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

    return {
        "title": entry.title,
        "link": entry.link,
        "pubDate": datetime(*entry.published_parsed[:6]),
        "source": source
    }


def handle_twitter_urls(entry):
    """
    Handles the modification of Twitter URLs in the feed entry.
    """
    entry.title = re.sub(r'^R to @\w+: ', '', entry.title)
    entry.link = re.sub(r'https?://nitter\.[^/]+', 'https://twitter.com', entry.link)
    return entry


def fetch_session_info(source: str):
    """
    Fetches session information from the database and sends a prompt to the LLM.
    """
    db = next(get_db())
    items = fetch_items_from_db(db, source)
    items_str = "\n".join([f"Title: {item.title}, Date: {item.pubDate}" for item in items])
    current_date = datetime.now().strftime("%B %d, %Y")
    prompt_template = get_prompt_template(source)
    prompt = prompt_template.format(current_date=current_date) + "\n\n" + items_str

    next_meeting_date = send_prompt(prompt)
    if not re.search(r'unknown', next_meeting_date, re.IGNORECASE):
        update_meeting_info(db, source, next_meeting_date)


def fetch_items_from_db(db: Session, source: str):
    """
    Fetches items from the database based on the source.
    """
    return db.query(RSSItem)\
             .filter(RSSItem.source == source)\
             .order_by(desc(RSSItem.pubDate))\
             .limit(15)\
             .all()


def get_prompt_template(source: str) -> str:
    """
    Retrieves the appropriate prompt template based on the source.
    """
    filename = SENATE_PROMPT_FILE if source == "senateppg-twitter" else HOUSE_PROMPT_FILE
    with open(filename, 'r') as file:
        return file.read()
