#!/usr/bin/env python3
# newsapi_scraper.py
# Fetch yesterday's NewsAPI.org headlines for S&P 500 companies (up to 100 requests/day)

import os
import json
import time
import requests
import datetime
import pandas as pd

API_KEY = 'e571f2b08136491994bde473746cf058'

WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
NEWSAPI_URL = 'https://newsapi.org/v2/everything'

# Number of tickers per query to stay within 100 requests (approx. 500 symbols / 5 per group = 100 requests)
GROUP_SIZE = 5
# Minimum delay between requests (seconds) to avoid hitting rate limits
REQUEST_DELAY = 1
# Maximum number of retries on 429 errors
MAX_RETRIES = 5


def fetch_sp500_tickers():
    """
    Scrape the current list of S&P 500 tickers from Wikipedia.
    """
    tables = pd.read_html(WIKI_URL)
    df = tables[0]
    return df['Symbol'].tolist()


def chunk_list(items, size):
    """
    Yield successive chunks of length 'size' from 'items'.
    """
    for i in range(0, len(items), size):
        yield items[i:i + size]


def request_with_backoff(url, params):
    """
    Make a GET request with simple exponential backoff on HTTP 429.
    """
    retries = 0
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 429:
            if retries < MAX_RETRIES:
                wait = 2 ** retries
                print(f"Rate limit hit (429). Retrying in {wait} seconds...")
                time.sleep(wait)
                retries += 1
                continue
            else:
                response.raise_for_status()
        else:
            response.raise_for_status()
        return response.json()


def fetch_headlines_for_date(date, api_key):
    """
    Fetch articles for all S&P 500 companies for a given date.
    """
    tickers = fetch_sp500_tickers()
    all_articles = []

    # Format ISO datetime strings for NewsAPI
    from_param = date.strftime('%Y-%m-%dT00:00:00')
    to_param = date.strftime('%Y-%m-%dT23:59:59')

    for group in chunk_list(tickers, GROUP_SIZE):
        query = ' OR '.join(group)
        params = {
            'q': query,
            'language': 'en',
            'from': from_param,
            'to': to_param,
            'sortBy': 'publishedAt',
            'apiKey': api_key,
            'pageSize': 100
        }
        data = request_with_backoff(NEWSAPI_URL, params)
        articles = data.get('articles', [])
        all_articles.extend(articles)
        # Delay to respect rate limits
        time.sleep(REQUEST_DELAY)

    return all_articles


def save_articles(articles, date):
    """
    Save the raw JSON articles to data/raw/YYYY-MM-DD/headlines.json.
    """
    date_str = date.strftime('%Y-%m-%d')
    output_dir = os.path.join('data', 'raw', date_str)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'headlines.json')
    with open(output_path, 'w') as f:
        json.dump({
            'date': date_str,
            'articles': articles
        }, f, indent=2)

    print(f"Saved {len(articles)} articles to {output_path}")


def main():
    # Use UTC date for consistency; adjust if needed for local timezone
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    articles = fetch_headlines_for_date(yesterday, API_KEY)
    save_articles(articles, yesterday)


if __name__ == '__main__':
    main()
