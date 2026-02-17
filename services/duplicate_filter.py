from datetime import datetime
from typing import List


def save_news_items(conn, items: List[dict]) -> None:
    """Insert items into the `news` table using INSERT OR IGNORE to avoid duplicates.

    Expects a valid SQLite `conn` and item dicts with keys matching the DB columns.
    """
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in items:
        c.execute(
            """
            INSERT OR IGNORE INTO news
            (title, link, source, category, thumbnail, published, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("title", ""),
                item.get("link", ""),
                item.get("source", ""),
                item.get("category", ""),
                item.get("thumbnail", ""),
                item.get("published", ""),
                now,
            ),
        )

    conn.commit()
