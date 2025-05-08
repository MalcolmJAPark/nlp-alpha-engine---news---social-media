#!/usr/bin/env python3
"""
NewsAPI.org scraper: Automatically fetches yesterday's headlines (English, sorted by publication date)
and saves raw JSON responses in data/raw/YYYY-MM-DD/.
Runs once daily at 01:00 local time.
"""

import os
import requests
import datetime
import time
import json
import schedule

API_KEY = "e571f2b08136491994bde473746cf058"
BASE_URL = "https://newsapi.org/v2/everything"
PAGE_SIZE = 100       # maximum page size per request
MAX_REQUESTS = 100    # NewsAPI free plan limit per day


def fetch_headlines(page: int, date_str: str) -> dict:
    """
    Fetches a single page of articles from NewsAPI for a given page and date.
    """
    params = {
        "q":       "news",
        "from": date_str,
        "to": date_str,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": PAGE_SIZE,
        "page": page,
        "apiKey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


def save_response(data: dict, date_str: str, page: int) -> None:
    """
    Saves the JSON response to data/raw/YYYY-MM-DD/headlines_page_{page}.json
    """
    dir_path = os.path.join("data", "raw", date_str)
    os.makedirs(dir_path, exist_ok=True)
    file_name = f"headlines_page_{page}.json"
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved page {page} -> {file_path}")


def run_job():
    # Calculate yesterday's date in YYYY-MM-DD format
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    print(f"[{datetime.datetime.now().isoformat()}] Fetching headlines for {yesterday}...")

    for page in range(1, MAX_REQUESTS + 1):
        try:
            data = fetch_headlines(page, yesterday)
        except requests.HTTPError as e:
            print(f"HTTP error on page {page}: {e}")
            break

        if data.get("status") != "ok":
            print(f"API error on page {page}: {data}")
            break

        articles = data.get("articles", [])
        if not articles:
            print(f"No articles found on page {page}. Stopping.")
            break

        save_response(data, yesterday, page)

        if len(articles) < PAGE_SIZE:
            print("Retrieved all available articles.")
            break

        time.sleep(1)  # Be courteous to API

    print("Job done.")


def main():
    # Schedule the daily job at 01:00
    schedule.every().day.at("01:00").do(run_job)
    print("Scheduler started: job will run daily at 01:00 local time.")

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
