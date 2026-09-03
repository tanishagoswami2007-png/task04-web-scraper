# Task 04 - Automated Web Scraping & Data Extraction Pipeline

This project is an automated ETL-style scraper using **Python, Requests and BeautifulSoup**.

**Target:** Hacker News public website — https://news.ycombinator.com/

## Requirements covered

- Public web resource selected: Hacker News.
- Custom `User-Agent`, `Accept`, and `Accept-Language` headers.
- 1-second rate limiting between requests.
- Retry logic for HTTP 429, 500, 502, 503 and 504 errors.
- 15-second request timeout.
- BeautifulSoup HTML parsing.
- Transformation into structured records.
- CSV output containing title, URL, score, author and UTC scrape time.
- Automated summary statistics: record count, unique authors, average/highest/lowest score.

## Files

```text
task04-web-scraper/
├── scraper.py
├── requirements.txt
├── output.csv
└── README.md
```

## Run

```bash
pip install -r requirements.txt
python scraper.py
```

The script creates/updates `output.csv` and prints the summary report.

## Responsible scraping

The scraper uses a low request rate, timeout, retry handling and only requests the public page needed for this dataset.
