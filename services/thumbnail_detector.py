import requests
from bs4 import BeautifulSoup

PLACEHOLDER = "https://via.placeholder.com/300x200.png?text=No+Image"


def get_thumbnail(entry: dict) -> str:
    """Return thumbnail URL for a normalized entry dict.

    Priority:
    1. entry['media'] (if provided by RSS)
    2. image-type link in entry['links']
    3. scrape og:image from the article page
    4. fallback placeholder
    """
    # 1) media from feed
    media = entry.get("media")
    if media:
        return media

    # 2) check links for image mime-type
    for link in entry.get("links", []) or []:
        if link.get("type", "").startswith("image"):
            return link.get("href")

    # 3) try scraping og:image
    try:
        resp = requests.get(entry.get("link", ""), timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og.get("content")
    except Exception:
        pass

    # 4) fallback
    return PLACEHOLDER
