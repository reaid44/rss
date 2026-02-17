from flask import Flask, jsonify
import feedparser
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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


# -------------------------
# Thumbnail Detect
# -------------------------

def get_thumbnail(entry):
    # Method 1: RSS media
    if 'media_content' in entry:
        return entry.media_content[0]['url']

    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image'):
                return link.href

    # Method 2: Scrape og:image
    try:
        response = requests.get(entry.link, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        og = soup.find("meta", property="og:image")
        if og:
            return og["content"]
    except:
        pass

    # Fallback
    return "https://via.placeholder.com/300x200.png?text=No+Image"


# -------------------------
# Fetch RSS
# -------------------------

def fetch_news():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    for category, feeds in RSS_FEEDS.items():
        for source_name, url in feeds:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:
                title = entry.title
                link = entry.link
                published = entry.get("published", "")
                thumbnail = get_thumbnail(entry)

                try:
                    c.execute("""
                        INSERT INTO news (title, link, source, category, thumbnail, published, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        title,
                        link,
                        source_name,
                        category,
                        thumbnail,
                        published,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    conn.commit()
                except:
                    pass  # duplicate ignore

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

    result = []
    for row in rows:
        result.append({
            "title": row[0],
            "link": row[1],
            "source": row[2],
            "category": row[3],
            "thumbnail": row[4],
            "published": row[5]
        })

        return render_template("index.html", news=news_list)

    return jsonify(result)


@app.route("/update")
def update():
    fetch_news()
    return "News Updated Successfully!"


if __name__ == "__main__":
    init_db()
    fetch_news()
    app.run(debug=True)
