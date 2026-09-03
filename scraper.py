import csv
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://news.ycombinator.com/"
OUTPUT_FILE = Path("output.csv")
REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3
MAX_ITEMS = 30


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    retry = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_page(session, url):
    response = session.get(url, timeout=15)
    response.raise_for_status()
    time.sleep(REQUEST_DELAY_SECONDS)
    return response.text


def parse_news(html, limit=MAX_ITEMS):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for row in soup.select("tr.athing")[:limit]:
        title_tag = row.select_one("span.titleline > a")
        if not title_tag:
            continue
        subtext = row.find_next_sibling("tr")
        score_tag = subtext.select_one(".score") if subtext else None
        user_tag = subtext.select_one(".hnuser") if subtext else None

        score = 0
        if score_tag:
            try:
                score = int(score_tag.get_text(strip=True).split()[0])
            except ValueError:
                pass

        link = title_tag.get("href", "")
        if link.startswith("item?id="):
            link = BASE_URL + link

        records.append({
            "title": title_tag.get_text(" ", strip=True),
            "url": link,
            "score": score,
            "author": user_tag.get_text(strip=True) if user_tag else "unknown",
        })
    return records


def save_csv(records, filename=OUTPUT_FILE):
    fields = ["scraped_at_utc", "title", "url", "score", "author"]
    timestamp = datetime.now(timezone.utc).isoformat()
    with Path(filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({"scraped_at_utc": timestamp, **record})


def generate_report(records):
    if not records:
        return "No records were scraped."
    scores = [r["score"] for r in records]
    return (
        "\n=== Automated Scraping Summary ===\n"
        f"Records scraped: {len(records)}\n"
        f"Unique authors: {len({r['author'] for r in records})}\n"
        f"Average score: {statistics.mean(scores):.2f}\n"
        f"Highest score: {max(scores)}\n"
        f"Lowest score: {min(scores)}\n"
        f"CSV output: {OUTPUT_FILE}\n"
    )


def main():
    session = create_session()
    html = fetch_page(session, BASE_URL)
    records = parse_news(html)
    save_csv(records)
    print(generate_report(records))


if __name__ == "__main__":
    main()
