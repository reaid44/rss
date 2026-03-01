from flask import Flask, render_template, request
import sqlite3
from services.rss_parser import parse_feeds
from services.thumbnail_detector import get_thumbnail
from services.duplicate_filter import save_news_items
from services.rss_feeds import RSS_FEEDS
from flask_caching import Cache   # caching রাখা হলো

app = Flask(__name__)
DATABASE = "news.db"

# Cache configuration
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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

def fetch_news():
    items = parse_feeds(RSS_FEEDS, max_entries=10)

    for item in items:
        item['thumbnail'] = get_thumbnail(item)

    conn = sqlite3.connect(DATABASE)
    save_news_items(conn, items)
    conn.close()

@app.route("/")
@cache.cached(timeout=60, query_string=True)   # cache 60 সেকেন্ডের জন্য
def home():
    # Infinity Scroll এর জন্য Pagination দরকার
    page = int(request.args.get("page", 1))   # default page = 1
    per_page = 10                             # প্রতি পেজে 10 নিউজ
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT title, link, source, category, thumbnail, published FROM news ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
    rows = c.fetchall()
    conn.close()

    grouped_news = {
        "Bangladesh": [],
        "International": [],
        "Technology": []
    }

    for row in rows:
        item = {
            "title": row[0],
            "link": row[1],
            "source": row[2],
            "category": row[3],
            "thumbnail": row[4],
            "published": row[5]
        }

        if item["category"] == "Bangladesh":
            grouped_news["Bangladesh"].append(item)
        elif item["category"] == "International":
            grouped_news["International"].append(item)
        elif item["category"] == "Technology":
            grouped_news["Technology"].append(item)

    return render_template("index.html", grouped_news=grouped_news, page=page)

@app.route("/update")
def update():
    fetch_news()
    cache.clear()   # cache clear করলে নতুন নিউজ আসবে
    return "News Updated Successfully!"

if __name__ == "__main__":
    init_db()
    fetch_news()
    app.run(debug=True)