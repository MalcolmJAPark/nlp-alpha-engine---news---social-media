#!/usr/bin/env python3
"""
NewsAPI.org scraper: Fetches yesterday's headlines (English, sorted by publication date)
and saves raw JSON responses in data/raw/YYYY-MM-DD/page_{n}.json.
Supports up to 100 requests/day (NewsAPI free tier limit).
"""

import os
import requests
import datetime
import time
import json

API_KEY = "e571f2b08136491994bde473746cf058"
BASE_URL = "https://newsapi.org/v2/everything"
PAGE_SIZE = 100       # maximum page size per request
MAX_REQUESTS = 100    # NewsAPI free plan limit per day


def fetch_headlines(page: int, date_str: str) -> dict:
    """
    Fetches a single page of articles from NewsAPI for a given page and date.
    """
    params = {
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
    Saves the JSON response to data/raw/YYYY-MM-DD/page_{page}.json
    """
    dir_path = os.path.join("data", "raw", date_str)
    os.makedirs(dir_path, exist_ok=True)
    file_name = f"headlines_page_{page}.json"
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved page {page} -> {file_path}")


def main():
    # Calculate yesterday's date in YYYY-MM-DD format
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    print(f"Fetching headlines for {yesterday}...")
    for page in range(1, MAX_REQUESTS + 1):
        try:
            data = fetch_headlines(page, yesterday)
        except requests.HTTPError as e:
            print(f"HTTP error on page {page}: {e}")
            break

        status = data.get("status")
        if status != "ok":
            print(f"API error on page {page}: {data}")
            break

        articles = data.get("articles", [])
        if not articles:
            print(f"No articles found on page {page}. Stopping.")
            break

        save_response(data, yesterday, page)

        # If fewer articles than page size, we've retrieved all for that day
        if len(articles) < PAGE_SIZE:
            print("Retrieved all available articles.")
            break

        # Be courteous to API; adjust sleep as needed
        time.sleep(1)

    print("Done.")


if __name__ == "__main__":
    main()
