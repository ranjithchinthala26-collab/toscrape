import json
import logging
import time
from http.server import BaseHTTPRequestHandler
from collections import Counter
from pathlib import Path

import pandas as pd

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import SCHEMA, clean_records
from processing.validation import validate_records
from processing.deduplication import deduplicate


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("pipeline")


def count_by_source(records):
    return dict(Counter(record.get("source") for record in records))


def main():
    start = time.perf_counter()
    logger.info("Starting scraping pipeline")

    books = BooksScraper().scrape()
    quotes = QuotesScraper().scrape()
    collected = books + quotes

    logger.info("Total records collected: %d", len(collected))

    cleaned = clean_records(collected)
    valid, rejected = validate_records(cleaned)
    unique, duplicates = deduplicate(valid)

    dataframe = pd.DataFrame(unique, columns=SCHEMA)

    dataframe.to_csv(
        OUTPUT_DIR / "final_dataset.csv",
        index=False,
        encoding="utf-8",
    )

    elapsed = round(time.perf_counter() - start, 2)

    summary = {
        "records_collected_per_source": count_by_source(collected),
        "total_records_collected": len(collected),
        "total_records_after_cleaning": len(cleaned),
        "records_rejected_during_validation": len(rejected),
        "validation_rejection_details": rejected,
        "duplicate_records_detected": len(duplicates),
        "duplicate_records_removed": len(duplicates),
        "final_record_count": len(unique),
        "execution_time_seconds": elapsed,
    }

    with open(
        OUTPUT_DIR / "summary_report.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    logger.info("Final records: %d", len(unique))
    logger.info("Rejected records: %d", len(rejected))
    logger.info("Duplicates removed: %d", len(duplicates))
    logger.info("Execution time: %.2f seconds", elapsed)
    logger.info("Pipeline completed successfully")


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function entry point.
    This does not run the scraper again.
    It exposes the existing generated summary as a health/status endpoint.
    """

    def do_GET(self):
        try:
            summary_file = OUTPUT_DIR / "summary_report.json"

            if summary_file.exists():
                with open(
                    summary_file,
                    "r",
                    encoding="utf-8",
                ) as file:
                    summary = json.load(file)

                response = {
                    "status": "healthy",
                    "project": "Multi-Source Web Scraping Pipeline",
                    "message": "Scraping assignment deployed successfully",
                    "records_collected": summary.get(
                        "total_records_collected"
                    ),
                    "final_record_count": summary.get(
                        "final_record_count"
                    ),
                    "duplicates_removed": summary.get(
                        "duplicate_records_removed"
                    ),
                }

            else:
                response = {
                    "status": "healthy",
                    "project": "Multi-Source Web Scraping Pipeline",
                    "message": "Application deployed successfully, "
                    "but summary_report.json is not available.",
                }

            body = json.dumps(response).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.end_headers()

            self.wfile.write(body)

        except Exception as error:
            body = json.dumps(
                {
                    "status": "error",
                    "message": str(error),
                }
            ).encode("utf-8")

            self.send_response(500)
            self.send_header(
                "Content-Type",
                "application/json",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.end_headers()

            self.wfile.write(body)


if __name__ == "__main__":
    main()