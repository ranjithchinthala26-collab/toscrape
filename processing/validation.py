from urllib.parse import urlparse


def is_valid_url(value):
    try:
        parsed = urlparse(str(value))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def validate_record(record):
    errors = []

    if not record.get("source"):
        errors.append("missing source")

    if not record.get("source_url") or not is_valid_url(record["source_url"]):
        errors.append("invalid source_url")

    if not record.get("name_or_title"):
        errors.append("missing name_or_title")

    price = record.get("price")
    if price is not None:
        try:
            if float(price) < 0:
                errors.append("negative price")
        except (TypeError, ValueError):
            errors.append("non-numeric price")

    rating = record.get("rating")
    if rating is not None:
        try:
            if not 1 <= float(rating) <= 5:
                errors.append("rating outside 1-5")
        except (TypeError, ValueError):
            errors.append("invalid rating")

    allowed_sources = {"Books to Scrape", "Quotes to Scrape"}
    if record.get("source") not in allowed_sources:
        errors.append("unrecognized source")

    return len(errors) == 0, errors


def validate_records(records):
    valid = []
    rejected = []

    for record in records:
        ok, errors = validate_record(record)
        if ok:
            valid.append(record)
        else:
            rejected.append({"record": record, "errors": errors})

    return valid, rejected
