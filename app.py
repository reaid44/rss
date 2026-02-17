from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

from services.rss_parser import parse_feeds
from services.thumbnail_detector import get_thumbnail
from services.duplicate_filter import save_news_items

app = Flask(__name__)

DATABASE = "news.db"

RSS_FEEDS = {
    "Bangladesh": [
        ("Prothom Alo", "https://www.prothomalo.com/feed"),
        ("bdnews24", "https://bdnews24.com/rss")
    ],
    "International": [
        ("BBC Bangla", "https://www.bbc.com/bengali/index.xml")
    ]
}

# -------------------------
# Database Setup
# -------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            source TEXT,
            category TEXT,
            thumbnail TEXT,
            published TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# Thumbnail detection moved to `services/thumbnail_detector.py`


# -------------------------
# Fetch RSS (delegates to services)
# -------------------------

def fetch_news():
    items = parse_feeds(RSS_FEEDS, max_entries=10)

    # ensure each item has a thumbnail (service handles media/link/scrape)
    for item in items:
        item['thumbnail'] = get_thumbnail(item)

    conn = sqlite3.connect(DATABASE)
    save_news_items(conn, items)
    conn.close()


# -------------------------
# API Route
# -------------------------

@app.route("/")
def home():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT title, link, source, category, thumbnail, published FROM news ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()

    news_list = []
    for row in rows:
        news_list.append({
            "title": row[0],
            "link": row[1],
            "source": row[2],
            "category": row[3],
            "thumbnail": row[4],
            "published": row[5]
        })

    # render template with the news list
    return render_template("index.html", news=news_list)


@app.route("/update")
def update():
    fetch_news()
    return "News Updated Successfully!"


if __name__ == "__main__":
    init_db()
    fetch_news()
    app.run(debug=True)
