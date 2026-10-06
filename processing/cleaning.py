import re
from urllib.parse import urlparse

import pandas as pd

SCHEMA = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "availability", "scraped_at"
]


def clean_text(value):
    if value is None or pd.isna(value):
        return None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None


def clean_price(value):
    if value is None or pd.isna(value):
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value):
    if value is None or pd.isna(value):
        return None
    try:
        rating = float(value)
        return int(rating) if rating.is_integer() else rating
    except (TypeError, ValueError):
        return None


def valid_url(value):
    if not value:
        return False
    parsed = urlparse(str(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def clean_records(records):
    cleaned = []

    for record in records:
        item = {field: record.get(field) for field in SCHEMA}

        for field in ["source", "source_url", "name_or_title", "category",
                      "author", "tags", "description", "availability"]:
            item[field] = clean_text(item[field])

        item["price"] = clean_price(item["price"])
        item["rating"] = clean_rating(item["rating"])

        if item["source"] == "Quotes to Scrape" and item["tags"]:
            tags = [clean_text(tag) for tag in item["tags"].split(",")]
            item["tags"] = ", ".join(tag for tag in tags if tag)

        cleaned.append(item)

    return cleaned
