# Multi-Source Web Scraping & Data Consolidation

## 1. Overview

This project implements the technical assessment using Python.

It collects data from:

1. Books to Scrape - https://books.toscrape.com/
2. Quotes to Scrape - https://quotes.toscrape.com/

The pipeline performs:

Scraping -> Cleaning -> Validation -> Deduplication -> Consolidation -> CSV/JSON output

## 2. Python Version

Recommended: Python 3.11 or newer.

## 3. Project Structure

```text
scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── output/
├── logs/
├── tests/
│   └── test_processing.py
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 4. Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run

```bash
python main.py
```

The scraper automatically follows the `Next` pagination link until there are no more pages.

## 6. Data Model

The common schema is:

- source
- source_url
- name_or_title
- category
- price
- rating
- author
- tags
- description
- availability
- scraped_at

Fields that do not apply to a source are stored as null/empty values. No data is invented.

## 7. Scraping Approach

Requests is used for HTTP requests and BeautifulSoup is used for HTML parsing.

Separate scraper classes are used for each source so source-specific selectors remain isolated.

Books use the product listing pages and then request each product detail page to obtain fields such as category, description, availability, and rating.

Quotes are extracted from each quote listing page.

## 8. Pagination

Pagination is not hard-coded.

For each source, the scraper looks for:

```html
<li class="next"><a href="...">next</a></li>
```

When the link exists, its URL is followed. When it does not exist, scraping stops.

## 9. Cleaning

Cleaning includes:

- whitespace normalization
- price conversion to numeric values
- rating conversion
- tag normalization
- empty-value normalization
- URL validation

Cleaning is implemented separately from scraping.

## 10. Validation

Records are checked for:

- recognizable source
- valid-looking source URL
- required title/name
- non-negative numeric prices
- ratings between 1 and 5

Invalid records are rejected and included in the summary report.

## 11. Deduplication

Duplicates are detected using a normalized key based on:

- source
- name_or_title
- author

Text is case-folded and whitespace is normalized first.

For example:

```text
" Example Book "
"EXAMPLE BOOK"
```

are treated as equivalent when the other key fields are the same.

The source is included in the key so records from different websites are not accidentally considered duplicates.

## 12. Error Handling

The scraper handles:

- connection failures
- HTTP errors
- timeouts
- missing HTML elements
- unexpected parsing errors
- individual page failures

Requests are retried up to three times using a small exponential backoff.

Logging is written to:

```text
logs/scraper.log
```

The pipeline attempts to continue where reasonably possible instead of terminating on the first page-level problem.

## 13. Output

After execution:

```text
output/final_dataset.csv
output/summary_report.json
```

The JSON summary contains:

- records collected per source
- total records collected
- records after cleaning
- validation rejections
- duplicate records detected
- duplicate records removed
- final record count
- execution time

## 14. Tests

Run:

```bash
pytest
```

The tests cover text cleaning, price conversion, validation, invalid ratings, and duplicate detection.

## 15. Assumptions

- The two provided websites remain available and retain their general HTML structure.
- Public pages can be requested without authentication.
- Ratings on Books to Scrape are represented by one-to-five star classes.
- Missing source-specific fields are represented by null/empty values.

## 16. Known Limitations

- HTML selector changes on the target websites could require scraper updates.
- This is a take-home assessment implementation rather than a full production scraping platform.
- The current version writes results to CSV/JSON rather than a database.
- Scraping is sequential to keep request volume reasonable and the implementation easy to understand.

## 17. AI Usage

AI assistance was used during development. Details are documented in `AI_USAGE.md`.
