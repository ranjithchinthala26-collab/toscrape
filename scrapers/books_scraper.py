import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
logger = logging.getLogger(__name__)


class BooksScraper:
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
                logger.warning("Books request failed (%s/%s): %s", attempt, self.retries, exc)
                if attempt < self.retries:
                    time.sleep(2 ** (attempt - 1))
        raise last_error

    @staticmethod
    def parse_rating(class_names):
        ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        for item in class_names:
            if item in ratings:
                return ratings[item]
        return None

    def parse_detail(self, url):
        try:
            html = self.fetch(url)
            soup = BeautifulSoup(html, "html.parser")

            product = soup.select_one(".product_page")
            if not product:
                raise ValueError("Product page structure not found")

            title = soup.select_one("h1")
            price = soup.select_one(".price_color")
            availability = soup.select_one(".availability")
            rating_node = soup.select_one(".star-rating")
            category_node = soup.select("ul.breadcrumb li a")
            description = soup.select_one("#product_description + p")

            category = None
            if len(category_node) >= 3:
                category = category_node[-1].get_text(strip=True)

            rating = None
            if rating_node:
                rating = self.parse_rating(rating_node.get("class", []))

            return {
                "source": "Books to Scrape",
                "source_url": url,
                "name_or_title": title.get_text(strip=True) if title else None,
                "category": category,
                "price": price.get_text(strip=True) if price else None,
                "rating": rating,
                "author": None,
                "tags": None,
                "description": description.get_text(" ", strip=True) if description else None,
                "availability": availability.get_text(" ", strip=True) if availability else None,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Could not parse book detail %s: %s", url, exc)
            return None

    def scrape(self):
        records = []
        page_url = BASE_URL

        while page_url:
            logger.info("Scraping books page: %s", page_url)
            try:
                html = self.fetch(page_url)
                soup = BeautifulSoup(html, "html.parser")
                products = soup.select("article.product_pod")

                if not products:
                    logger.warning("No books found on %s", page_url)
                    break

                for product in products:
                    link = product.select_one("h3 a")
                    if not link or not link.get("href"):
                        logger.warning("Book link missing on %s", page_url)
                        continue

                    detail_url = urljoin(page_url, link["href"])
                    record = self.parse_detail(detail_url)
                    if record:
                        records.append(record)
                    time.sleep(self.delay)

                next_link = soup.select_one("li.next a")
                page_url = urljoin(page_url, next_link["href"]) if next_link else None
                time.sleep(self.delay)

            except Exception as exc:
                logger.error("Books page failed: %s | %s", page_url, exc)
                next_link = None
                try:
                    next_link = BeautifulSoup(html, "html.parser").select_one("li.next a")
                except Exception:
                    pass
                if next_link:
                    page_url = urljoin(page_url, next_link["href"])
                else:
                    page_url = None

        logger.info("Books records collected: %d", len(records))
        return records
