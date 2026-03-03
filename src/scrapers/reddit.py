import time
import requests
from datetime import datetime, timezone, timedelta


SUBREDDITS = ["MachineLearning", "LocalLLaMA", "UXDesign", "ethereum"]
POSTS_PER_SUB = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def scrape_reddit() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    posts = []

    for sub_name in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub_name}/top.json?limit={POSTS_PER_SUB}&t=week"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Warning: could not fetch r/{sub_name} ({e}), skipping.")
            continue

        for child in data["data"]["children"]:
            post = child["data"]
            created = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)
            if created < cutoff:
                continue

            body = (post.get("selftext") or "")[:300].replace("\n", " ").strip()
            posts.append({
                "title": post["title"],
                "url": f"https://reddit.com{post['permalink']}",
                "snippet": body,
                "source": f"r/{sub_name}",
                "type": "reddit",
            })

        time.sleep(1)  # be polite between subreddit requests

    return posts
