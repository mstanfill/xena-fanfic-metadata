"""Parse Athenaeum search results pages 1-2 and print a sample for review.

Reads the copies saved by `fanfic-verify-athenaeum`. Any page not saved yet
is downloaded first (up to 2 requests, plus robots.txt), so run the verify
script first if you want this to stay offline. Writes every parsed record to
<data folder>/athenaeum_sample_output.json.

    fanfic-sample-athenaeum          (or: python -m fanfic_scraper.scripts.run_athenaeum_sample)
"""
import dataclasses
import json
import sys

from fanfic_scraper.discover.athenaeum import discover_athenaeum
from fanfic_scraper.fetch import default_data_dir
from fanfic_scraper.parse.athenaeum import parse_athenaeum_search_page


def main():
    pages = discover_athenaeum(max_pages=2)
    records = [r for page in pages for r in parse_athenaeum_search_page(page.body, page.url)]

    print(f"Parsed {len(records)} records from {len(pages)} Athenaeum search page(s)")
    print()
    sample = records[:10]
    print(json.dumps([dataclasses.asdict(r) for r in sample], indent=2, ensure_ascii=False))

    out_path = default_data_dir() / "athenaeum_sample_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(r) for r in records], f, indent=2, ensure_ascii=False)
    print()
    print(f"Full output written to {out_path} ({len(records)} records)")


if __name__ == "__main__":
    sys.exit(main())
