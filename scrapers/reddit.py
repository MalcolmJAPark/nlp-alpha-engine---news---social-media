#!/usr/bin/env python3
"""
Reddit scraper: Streams new posts from r/stocks, r/wallstreetbets, r/investing (1 request/sec throttle)
and saves each post's raw JSON to data/raw/YYYY-MM-DD/reddit_stream.json. Creates a new folder/file daily.
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
            # Determine date string for this submission
            timestamp = datetime.datetime.fromtimestamp(submission.created_utc)
            date_str = timestamp.date().isoformat()  # YYYY-MM-DD

            # Prepare directory and file path
            dir_path = os.path.join("data", "raw", date_str)
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "reddit_stream.json")

            # Write raw JSON data
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(submission._data) + "\n")

            print(f"[{timestamp.isoformat()}] Saved {submission.id} to {file_path}")

            # Throttle to respect rate limit
            time.sleep(THROTTLE_SECONDS)

        except Exception as e:
            print(f"Error processing submission: {e}")
            time.sleep(THROTTLE_SECONDS)


def main():
    stream_submissions()


if __name__ == "__main__":
    main()
