import feedparser
from typing import List, Dict


def parse_feeds(rss_feeds: Dict[str, List], max_entries: int = 10) -> List[Dict]:
    """Parse configured RSS feeds and return a list of normalized entry dicts.

    Each dict contains: title, link, published, source, category, media, links
    """
    items = []

    for category, feeds in rss_feeds.items():
        for source_name, url in feeds:
            feed = feedparser.parse(url)

            for entry in getattr(feed, "entries", [])[:max_entries]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                published = entry.get("published", "") or entry.get("updated", "")

                # media content (if present in feed)
                media = None
                if "media_content" in entry:
                    try:
                        media = entry.media_content[0].get("url")
                    except Exception:
                        media = None

                links = getattr(entry, "links", []) or entry.get("links", [])

                items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": source_name,
                    "category": category,
                    "media": media,
                    "links": links,
                })

    return items
