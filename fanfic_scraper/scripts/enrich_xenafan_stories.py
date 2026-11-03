"""Fetch part 1 of each xenafan story and add its header block
(disclaimer, warnings, sequel notes, author email) to the titles.html
records.

Two phases: a fetch phase that only fills the disk cache (resumable --
saved pages are never downloaded again), then a parse phase that reads only
from the cache. Makes network requests for every story page not saved yet,
plus titles.html if it is not saved.

    fanfic-enrich-xenafan            # sample: ~6 varied stories
    fanfic-enrich-xenafan --all      # full pass, ~1,450 requests (~2.5 h)

Run the sample first and review <data folder>/xenafan_enriched_sample.json
before running --all.
"""
import argparse
import dataclasses
import json
import sys
from urllib.parse import urljoin

from fanfic_scraper.discover.xenafan import TITLES_URL, discover_xenafan
from fanfic_scraper.fetch import XENAFAN, FetchError, build_default_fetcher, default_data_dir
from fanfic_scraper.fetch.urlnorm import normalize_url
from fanfic_scraper.parse.xenafan import parse_xenafan_titles
from fanfic_scraper.parse.xenafan_story import apply_story_header, parse_xenafan_story

MAX_CONSECUTIVE_FAILURES = 3


def part1_url(record):
    """Absolute URL of the story's first part, or None for external/lost stories."""
    if record.external_url or record.status == "removed":
        return None
    href = record.parts[0].url if record.parts else record.source_id
    if not href or href.startswith(f"{record.source_site}:"):
        return None
    return urljoin(TITLES_URL, href)


def pick_sample(targets, size):
    """One story per content directory first (content/, content2/, quill/...),
    so the sample covers the different eras of markup."""
    by_dir = {}
    for record, url in targets:
        by_dir.setdefault(url.rsplit("/", 1)[0], []).append((record, url))
    picked = [group[0] for group in by_dir.values()][:size]
    for target in targets:
        if len(picked) >= size:
            break
        if target not in picked:
            picked.append(target)
    return picked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="enrich every story (~1,450 requests)")
    parser.add_argument("--sample-size", type=int, default=6)
    args = parser.parse_args(argv)

    fetcher = build_default_fetcher(XENAFAN)
    records = parse_xenafan_titles(discover_xenafan(fetcher).body)
    targets = [(r, u) for r in records if (u := part1_url(r))]
    if not args.all:
        targets = pick_sample(targets, args.sample_size)
    print(f"{len(targets)} story pages to enrich ({len(records)} records in index)")

    # Fetch phase: fills the cache only.
    consecutive_failures = 0
    for i, (_record, url) in enumerate(targets, 1):
        if fetcher.get_cached(url) is not None:
            continue
        try:
            fetcher.fetch(url)
            consecutive_failures = 0
            print(f"[{i}/{len(targets)}] fetched {url}")
        except FetchError as exc:
            consecutive_failures += 1
            print(f"[{i}/{len(targets)}] FAILED {url}: {exc}")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"Stopping: {consecutive_failures} failures in a row from {XENAFAN.host}. "
                      "Re-run later to resume from the cache.")
                break

    # Parse phase: reads only from the cache.
    enriched = []
    for record, url in targets:
        cached = fetcher.get_cached(url)
        if cached is None or cached.status != 200:
            continue
        header = parse_xenafan_story(cached.body, cached.url)
        apply_story_header(record, header, normalize_url(url, XENAFAN)[0])
        enriched.append(record)

    out_records = records if args.all else enriched
    out_path = default_data_dir() / ("xenafan_enriched.json" if args.all else "xenafan_enriched_sample.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(r) for r in out_records], f, indent=2, ensure_ascii=False)

    for record in enriched[:args.sample_size]:
        print()
        print(f"== {record.title} by {', '.join(record.authors)}")
        print(record.disclaimer_text or "(no header found)")
        if record.notes:
            print(f"-- notes: {record.notes}")
    print()
    print(f"Enriched {len(enriched)} of {len(targets)} stories; wrote {out_path}")


if __name__ == "__main__":
    sys.exit(main())
