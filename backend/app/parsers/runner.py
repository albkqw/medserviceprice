"""CLI entry point for running parsers.

Usage:
    python -m app.parsers.runner kdl
    python -m app.parsers.runner kdl --dry-run
"""

import asyncio
import logging
import sys

from app.parsers.sources.kdl import KDLParser
from app.parsers.storage import save_items

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

_PARSERS = {
    "kdl": KDLParser,
}


async def run(slug: str, dry_run: bool = False) -> None:
    parser_cls = _PARSERS.get(slug)
    if parser_cls is None:
        print(f"Unknown parser: {slug!r}. Available: {list(_PARSERS)}", file=sys.stderr)
        sys.exit(1)

    parser = parser_cls()
    print(f"Running parser: {slug}")
    items = await parser.parse()
    print(f"Fetched {len(items)} items")

    if dry_run:
        for item in items[:5]:
            print(f"  {item.raw_clinic_name} | {item.raw_service_name} | {item.raw_price} {item.raw_currency}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
        return

    stats = await save_items(items, source_slug=slug)
    print(f"Saved: {stats['saved']}  Skipped (duplicates): {stats['skipped']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m app.parsers.runner <parser_slug> [--dry-run]", file=sys.stderr)
        sys.exit(1)

    slug = args[0]
    dry_run = "--dry-run" in args
    asyncio.run(run(slug, dry_run=dry_run))
