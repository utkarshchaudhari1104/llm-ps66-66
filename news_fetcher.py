# news_fetcher.py - get headlines from an RSS feed (or the offline sample file)
import json, re
from html import unescape
from pathlib import Path
import feedparser

SAMPLE_FILE = Path(__file__).with_name("sample_news.json")

def clean_html(text: str) -> str:
    """Strip tags/entities from RSS descriptions."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()

def fetch_feed(url: str, limit: int = 10) -> list[dict]:
    """Return [{'title','description','link','published'}]. Raises RuntimeError if the feed is empty."""
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:limit]:
        items.append({
            "title": clean_html(e.get("title", "")),
            "description": clean_html(e.get("summary", "")),
            "link": e.get("link", ""),
            "published": e.get("published", ""),
        })
    if not items:
        raise RuntimeError("No headlines received (check internet or try another feed).")
    return items

def load_sample(limit: int = 10) -> list[dict]:
    """Offline demo headlines so the app can always be demonstrated."""
    return json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))[:limit]
