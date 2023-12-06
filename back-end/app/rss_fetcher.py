import feedparser
from datetime import datetime

def fetch_rss_data(rss_url, source):
    try:
        parsed_data = feedparser.parse(rss_url)
        items = []

        for entry in parsed_data.entries:
            if hasattr(entry, 'title') and hasattr(entry, 'link') and hasattr(entry, 'published_parsed'):
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "pubDate": datetime(*entry.published_parsed[:6]),
                    "source": source
                })
        return items
    except Exception:
        return []
