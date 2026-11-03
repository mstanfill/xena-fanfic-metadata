"""Parse the Academy author index and 5 sample author pages, and print the
records for review.

Reads the copies saved by `fanfic-verify-academy`. Any page not saved yet is
downloaded first (up to 6 requests, plus robots.txt), so run the verify
script first if you want this to stay offline. Writes the parsed records to
<data folder>/academy_sample_output.json.

    fanfic-sample-academy            (or: python -m fanfic_scraper.scripts.run_academy_sample)
"""
import dataclasses
import json
import sys

from fanfic_scraper.discover.academy import discover_academy
from fanfic_scraper.fetch import ACADEMY, default_data_dir
from fanfic_scraper.fetch.urlnorm import normalize_url
from fanfic_scraper.parse.academy import parse_author_page


def build_display_names_by_normalized_url(entries):
    """Map each entry's normalized author-page URL to its display names.

    Entry URLs are stored as given (from the raw index, scheme/encoding
    as-is). Sample
    page URLs returned by the fetcher have already been normalized (e.g.
    scheme forced to the site's configured scheme). Normalizing both sides
    through the same function lets callers match them regardless of those
    differences.
    """
    return {normalize_url(e.url, ACADEMY)[0]: e.display_names for e in entries}


def lookup_display_names(by_url, page_url):
    return by_url.get(normalize_url(page_url, ACADEMY)[0], [])


def main():
    index_page, entries, sample_pages = discover_academy()
    by_url = build_display_names_by_normalized_url(entries)

    records = []
    for page in sample_pages:
        display_names = lookup_display_names(by_url, page.url)
        records.extend(parse_author_page(page.body, page.url, display_names))

    print(f"{len(entries)} unique author URLs in the index")
    print(f"Parsed {len(records)} records from {len(sample_pages)} sample author page(s)")
    print()
    print(json.dumps([dataclasses.asdict(r) for r in records], indent=2, ensure_ascii=False))

    out_path = default_data_dir() / "academy_sample_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(r) for r in records], f, indent=2, ensure_ascii=False)
    print()
    print(f"Full sample output written to {out_path} ({len(records)} records)")


if __name__ == "__main__":
    sys.exit(main())
