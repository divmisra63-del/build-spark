import sys
from dotenv import load_dotenv

load_dotenv()

from scrapers.hackernews import scrape_hackernews
from scrapers.youtube import scrape_youtube
from curator import curate
from emailer import send_email


def main():
    print("Scraping Hacker News...")
    hn_posts = scrape_hackernews()
    print(f"  Found {len(hn_posts)} Hacker News posts")

    print("Scraping YouTube...")
    yt_videos = scrape_youtube()
    print(f"  Found {len(yt_videos)} YouTube videos")

    all_items = hn_posts + yt_videos
    if not all_items:
        print("No items scraped. Exiting.")
        sys.exit(1)

    print(f"Curating {len(all_items)} items with Claude...")
    ideas = curate(all_items)
    print(f"  Got {len(ideas)} ideas")

    print("Sending email...")
    send_email(ideas)
    print("Done.")


if __name__ == "__main__":
    main()
