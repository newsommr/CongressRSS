import pytz
from datetime import datetime
import logging
import requests

RSS_FEEDS = [
    ("https://rules.house.gov/rss.xml", "house-rules-committee"),
    (
        "https://www.whitehouse.gov/briefing-room/legislation/feed/",
        "white-house-legislation",
    ),
    (
        "https://www.whitehouse.gov/briefing-room/presidential-actions/feed/rss",
        "white-house-presidential-actions",
    ),
    ("https://twiiit.com/SenatePPG/rss", "senateppg-twitter"),
    ("https://twiiit.com/HouseDailyPress/rss", "housedailypress-twitter"),
    (
        "https://www.dsca.mil/press-media/major-arms-sales/feed",
        "dsca-major-arms-sales",
    ),
]

def convert_to_utc(date, timezone):
    try:
        local_tz = pytz.timezone(timezone)
        local_dt = local_tz.localize(date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt
    except Exception as e:
        logging.error(
            f"Error attempting to convert {date} to UTC with the {timezone} timezone: {e}"
        )
        return None

def current_time():
    print(datetime.now(pytz.utc))
    return datetime.now(pytz.utc)

def fetch(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None
