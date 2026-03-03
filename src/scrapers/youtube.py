import os
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build


SEARCH_QUERIES = [
    "build AI app tutorial beginner",
    "LLM project for beginners",
    "Claude API project tutorial",
]
RESULTS_PER_QUERY = 5


def scrape_youtube() -> list[dict]:
    youtube = build("youtube", "v3", developerKey=os.environ["YOUTUBE_API_KEY"])

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    videos = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        response = (
            youtube.search()
            .list(
                part="snippet",
                q=query,
                type="video",
                order="relevance",
                publishedAfter=cutoff,
                maxResults=RESULTS_PER_QUERY,
            )
            .execute()
        )

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            if video_id in seen_ids:
                continue
            seen_ids.add(video_id)

            snippet = item["snippet"]
            description = snippet.get("description", "")[:300].replace("\n", " ").strip()

            videos.append({
                "title": snippet["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "snippet": description,
                "source": snippet.get("channelTitle", "YouTube"),
                "type": "youtube",
            })

    return videos
