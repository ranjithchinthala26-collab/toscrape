import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
logger = logging.getLogger(__name__)


class QuotesScraper:
    def __init__(self, delay=0.2, timeout=15, retries=3):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "scraping-assignment/1.0 (educational project)"
        })

    def fetch(self, url):
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                last_error = exc
                logger.warning("Quotes request failed (%s/%s): %s", attempt, self.retries, exc)
                if attempt < self.retries:
                    time.sleep(2 ** (attempt - 1))
        raise last_error

    def scrape(self):
        records = []
        page_url = BASE_URL

        while page_url:
            logger.info("Scraping quotes page: %s", page_url)
            try:
                html = self.fetch(page_url)
                soup = BeautifulSoup(html, "html.parser")
                quote_blocks = soup.select("div.quote")

                if not quote_blocks:
                    logger.warning("No quotes found on %s", page_url)
                    break

                for block in quote_blocks:
                    text_node = block.select_one("span.text")
                    author_node = block.select_one("small.author")
                    tags = [
                        tag.get_text(strip=True)
                        for tag in block.select("div.tags a.tag")
                    ]

                    records.append({
                        "source": "Quotes to Scrape",
                        "source_url": page_url,
                        "name_or_title": text_node.get_text(strip=True) if text_node else None,
                        "category": None,
                        "price": None,
                        "rating": None,
                        "author": author_node.get_text(strip=True) if author_node else None,
                        "tags": ", ".join(tags) if tags else None,
                        "description": None,
                        "availability": None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })

                next_link = soup.select_one("li.next a")
                page_url = urljoin(page_url, next_link["href"]) if next_link else None
                time.sleep(self.delay)

            except Exception as exc:
                logger.error("Quotes page failed: %s | %s", page_url, exc)
                page_url = None

        logger.info("Quotes records collected: %d", len(records))
        return records
