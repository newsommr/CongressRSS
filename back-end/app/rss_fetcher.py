import feedparser
from datetime import datetime
import re  # Import the regular expression module

def fetch_rss_data(rss_url, source):
    try:
        parsed_data = feedparser.parse(rss_url)
        items = []

        for entry in parsed_data.entries:
            if hasattr(entry, 'title') and hasattr(entry, 'link') and hasattr(entry, 'published_parsed'):
                # Check if 'nitter' is in the link
                if 'nitter' in entry.link:
                    entry = handle_twitter_urls(entry)

                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "pubDate": datetime(*entry.published_parsed[:6]),
                    "source": source
                })
        return items
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def handle_twitter_urls(entry):
    # Modify tweet title if it starts with "R to @blah:"
    entry.title = re.sub(r'^R to @\w+: ', '', entry.title)
    # Use regular expression to replace the nitter domain with twitter.com
    entry.link = re.sub(r'https?://nitter\.[^/]+', 'https://twitter.com', entry.link)
    return entry
