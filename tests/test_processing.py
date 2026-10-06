from processing.cleaning import clean_price, clean_text, clean_records
from processing.validation import validate_record
from processing.deduplication import deduplicate


def test_clean_text():
    assert clean_text("  Example   Book \n Title ") == "Example Book Title"


def test_clean_price():
    assert clean_price("£51.77") == 51.77


def test_valid_record():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/example_1/index.html",
        "name_or_title": "Example Book",
        "price": 10.5,
        "rating": 4,
    }
    ok, errors = validate_record(record)
    assert ok is True
    assert errors == []


def test_invalid_rating():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Example",
        "price": 10,
        "rating": 7,
    }
    ok, errors = validate_record(record)
    assert ok is False
    assert "rating outside 1-5" in errors


def test_deduplication_ignores_case_and_whitespace():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": " Example Book ",
            "author": None,
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "EXAMPLE BOOK",
            "author": None,
        },
    ]
    unique, duplicates = deduplicate(records)
    assert len(unique) == 1
    assert len(duplicates) == 1
