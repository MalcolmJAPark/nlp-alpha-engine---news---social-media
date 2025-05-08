#!/usr/bin/env python3
"""
Reddit scraper: Streams new posts from r/stocks, r/wallstreetbets, and r/investing at 1 request/sec throttle,
constructs a JSON object of key post fields, and appends each to a daily file under data/raw/YYYY-MM-DD/reddit_stream.json.
"""

import os
import time
import json
import datetime
import praw

# Reddit API credentials
CLIENT_ID = "dFVNmIpXcPd54hcK4RgAkQ"
CLIENT_SECRET = "ZGmmdCjGSzFEYnzsVcAt1MN3cToOUQ"
USER_AGENT = "Same_File_5521"

# Subreddits to stream
SUBREDDITS = ["stocks", "wallstreetbets", "investing"]
THROTTLE_SECONDS = 1  # 1 request per second


def stream_submissions():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    combined = "+".join(SUBREDDITS)
    subreddit = reddit.subreddit(combined)
    print(f"Starting stream for: {combined}")

    for submission in subreddit.stream.submissions():
        try:
            # Build timestamp and daily directory
            timestamp = datetime.datetime.fromtimestamp(submission.created_utc)
            date_str = timestamp.date().isoformat()
            dir_path = os.path.join("data", "raw", date_str)
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "reddit_stream.json")

            # Extract key fields for JSON
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "author": submission.author.name if submission.author else None,
                "created_utc": submission.created_utc,
                "subreddit": submission.subreddit.display_name,
                "url": submission.url,
                "num_comments": submission.num_comments,
                "score": submission.score,
                "selftext": submission.selftext
            }

            # Append to daily file
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(post_data, ensure_ascii=False) + "\n")

            print(f"[{timestamp.isoformat()}] Saved {submission.id} to {file_path}")
            time.sleep(THROTTLE_SECONDS)

        except Exception as e:
            print(f"Error processing submission {submission.id}: {e}")
            time.sleep(THROTTLE_SECONDS)


def main():
    stream_submissions()


if __name__ == "__main__":
    main()

