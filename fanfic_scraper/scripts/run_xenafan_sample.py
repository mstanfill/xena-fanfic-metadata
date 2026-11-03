"""Parse the xenafan titles.html index and print a sample for review.

Reads the copy of titles.html saved by `fanfic-verify-xenafan`. If it has not
been saved yet, it is downloaded first (1 request, plus robots.txt), so run
the verify script first if you want this to stay offline. Writes every
parsed record to <data folder>/xenafan_sample_output.json.

    fanfic-sample-xenafan            (or: python -m fanfic_scraper.scripts.run_xenafan_sample)
"""
import dataclasses
import json
import sys

from fanfic_scraper.discover.xenafan import discover_xenafan
from fanfic_scraper.fetch import default_data_dir
from fanfic_scraper.parse.xenafan import parse_xenafan_titles


def main():
    cached = discover_xenafan()
    records = parse_xenafan_titles(cached.body)

    print(f"Parsed {len(records)} records from xenafan titles.html")
    print()
    sample = records[:10]
    print(json.dumps([dataclasses.asdict(r) for r in sample], indent=2, ensure_ascii=False))

    out_path = default_data_dir() / "xenafan_sample_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(r) for r in records], f, indent=2, ensure_ascii=False)
    print()
    print(f"Full output written to {out_path} ({len(records)} records)")


if __name__ == "__main__":
    sys.exit(main())
