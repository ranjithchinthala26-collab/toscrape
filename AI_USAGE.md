# AI Usage

## Tool Used

Tool: ChatGPT

## Purpose

ChatGPT was used as an allowed coding assistant for:

- understanding the assignment requirements
- designing the project structure
- understanding HTML selectors
- creating an initial Requests + BeautifulSoup implementation
- designing the common data schema
- debugging and improving error handling
- designing cleaning and validation functions
- creating unit tests
- improving README documentation

## Representative Prompts

1. "Design a Python project structure for a multi-source web scraping assignment."
2. "Create a Requests and BeautifulSoup scraper with automatic pagination."
3. "How can I normalize price, rating, whitespace, and missing values?"
4. "Create duplicate detection that ignores whitespace and capitalization."
5. "Create unit tests for the cleaning, validation, and deduplication functions."

## AI-Assisted Areas

AI assistance was used for the initial structure and implementation of:

- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`
- `processing/cleaning.py`
- `processing/validation.py`
- `processing/deduplication.py`
- `main.py`
- tests
- documentation

## Human Review and Changes

The implementation was reviewed against the assignment requirements.

Important design decisions were checked manually:

- Both sources have separate scraper modules.
- Pagination follows the site's next-page link instead of hard-coding page numbers.
- Missing fields are not invented.
- Price and rating are normalized.
- Validation happens before final output.
- Duplicate detection normalizes whitespace and capitalization.
- Source information and original URLs are preserved.
- Request failures are retried and logged.
- The final output contains CSV and JSON summary files.

## Verification

The solution should be verified by:

1. Installing dependencies in a clean virtual environment.
2. Running `pytest`.
3. Running `python main.py`.
4. Checking `output/final_dataset.csv`.
5. Checking `output/summary_report.json`.
6. Reviewing `logs/scraper.log`.
7. Manually inspecting sample records from both sources.

The candidate remains responsible for understanding and explaining the final implementation.
