import json
import logging
import time
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
    dataframe.to_csv(OUTPUT_DIR / "final_dataset.csv", index=False, encoding="utf-8")

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

    with open(OUTPUT_DIR / "summary_report.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    logger.info("Final records: %d", len(unique))
    logger.info("Rejected records: %d", len(rejected))
    logger.info("Duplicates removed: %d", len(duplicates))
    logger.info("Execution time: %.2f seconds", elapsed)
    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()
