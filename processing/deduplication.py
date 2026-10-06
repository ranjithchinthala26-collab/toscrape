import re


def normalize_key(value):
    if value is None:
        return ""
    value = str(value).casefold()
    value = re.sub(r"\s+", " ", value).strip()
    return value


def deduplicate(records):
    seen = set()
    unique = []
    duplicates = []

    for record in records:
        # Source is included so unrelated records from different sources
        # are not considered duplicates merely because their text matches.
        key = (
            normalize_key(record.get("source")),
            normalize_key(record.get("name_or_title")),
            normalize_key(record.get("author")),
        )

        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
            unique.append(record)

    return unique, duplicates
