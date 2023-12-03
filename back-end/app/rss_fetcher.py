import feedparser
from datetime import datetime

def fetch_rss_data(rss_url):
    parsed_data = feedparser.parse(rss_url)
    items = []

    for entry in parsed_data.entries:
        items.append({
            "title": entry.title,
            "link": entry.link,
            "pubDate": datetime(*entry.published_parsed[:6])
        })
    
    return items
