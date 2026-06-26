import re


def normalize_text(s: str) -> str:
    """Canonical form used for all comparisons: lowercase, collapsed whitespace."""
    return re.sub(r"\s+", " ", s.lower().strip())


def strip_parentheses(s: str) -> str:
    """Remove parenthetical alternatives to get a shorter, looser form.

    'Натрийуретический гормон (NT-proBNP, N-terminal...)' → 'Натрийуретический гормон'
    Used as a secondary lookup key so the matcher can find a match even when
    two sources describe the same test with different abbreviation styles.
    """
    cleaned = re.sub(r"\s*\([^)]*\)", "", s).strip()
    return re.sub(r"\s+", " ", cleaned)


def parse_duration_days(raw_duration: str | None) -> int | None:
    """Extract the minimum integer from a raw duration string.

    '2 дней'   → 2
    '2-5 дней' → 2
    None       → None
    """
    if not raw_duration:
        return None
    match = re.search(r"\d+", raw_duration)
    return int(match.group()) if match else None
