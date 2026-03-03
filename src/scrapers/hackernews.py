import time
import requests
from datetime import datetime, timezone, timedelta


BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"Accept": "application/json"}

AI_KEYWORDS = [
    "llm", "gpt", "claude", "ai", "ml", "machine learning", "neural",
    "chatbot", "rag", "embedding", "vector", "agent", "langchain",
    "openai", "anthropic", "ollama", "mistral", "automation", "tutorial",
]

FETCH_PER_FEED = 50  # story IDs to scan per feed
MAX_ITEMS = 20


def _fetch_item(item_id: int) -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}/item/{item_id}.json", headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _is_ai_related(title: str) -> bool:
    return any(kw in title.lower() for kw in AI_KEYWORDS)


def scrape_hackernews() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    items = []
    seen_ids = set()

    # Show HN = people sharing what they built (always relevant)
    # Top stories filtered by AI keywords
    feeds = ["showstories", "topstories"]

    for feed in feeds:
        try:
            r = requests.get(f"{BASE_URL}/{feed}.json", headers=HEADERS, timeout=10)
            r.raise_for_status()
            story_ids = r.json()[:FETCH_PER_FEED]
        except Exception as e:
            print(f"  Warning: could not fetch HN {feed} ({e}), skipping.")
            continue

        for story_id in story_ids:
            if len(items) >= MAX_ITEMS:
                return items

            if story_id in seen_ids:
                continue

            item = _fetch_item(story_id)
            if not item or item.get("type") != "story":
                continue

            title = item.get("title", "")

            # For top stories, only keep AI-related ones
            if feed == "topstories" and not _is_ai_related(title):
                continue

            created = datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc)
            if created < cutoff:
                continue

            seen_ids.add(story_id)
            url = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
            # Self-posts (Show HN / Ask HN) have a text body
            snippet = (item.get("text") or "")[:300].replace("\n", " ").strip()

            items.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": "Hacker News",
                "type": "hackernews",
            })

            time.sleep(0.1)  # be polite between item fetches

    return items
