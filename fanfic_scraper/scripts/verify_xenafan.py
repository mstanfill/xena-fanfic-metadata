"""Live check for xenafan.com: robots.txt and the titles.html index.

Makes 2 requests (robots.txt, then titles.html) through the project fetcher,
so the politeness, robots and cache rules apply. Pages are saved to the data
folder; re-running reads titles.html from the saved copy, and only robots.txt
is requested again (it is checked once per run, never saved).

Findings from the live run (October 2026):
- robots.txt: no Disallow covers /fiction/ and no Crawl-delay, so the
  default 5-10 s politeness applies.
- titles.html: HTTP 200, about 340 KB. `requests` reports ISO-8859-1 (the
  Content-Type header has no charset), but the body is UTF-8 and declares
  <meta charset="utf-8">, so the parser prefers the declared charset.
- Markup is semantic HTML (`<div class="entry" data-s="...">` >
  `<div class="story">` > `a.t`/`span.t` title, optional `span.note` /
  `span.deadnote`, `span.by`, optional `div.parts`). There are exactly 1450
  `.entry` blocks, matching the page's "1450 stories by 508 bards" header.

    fanfic-verify-xenafan            (or: python -m fanfic_scraper.scripts.verify_xenafan)
"""
import sys

from fanfic_scraper.discover.xenafan import TITLES_URL
from fanfic_scraper.fetch import XENAFAN, build_default_fetcher


def main():
    fetcher = build_default_fetcher(XENAFAN)

    robots = fetcher.robots_for(XENAFAN.host)
    print(f"robots.txt for {XENAFAN.host}:")
    print(f"  disallow_prefixes = {robots.disallow_prefixes}")
    print(f"  crawl_delay       = {robots.crawl_delay}")
    print()

    cached = fetcher.fetch(TITLES_URL)
    print(f"Fetched {TITLES_URL}")
    print(f"  status      = {cached.status}")
    print(f"  charset     = {cached.charset}")
    print(f"  byte length = {len(cached.body)}")
    print()
    text_preview = cached.body.decode(cached.charset or "utf-8", errors="replace")
    print("First 2000 characters of decoded body (inspect tag structure here):")
    print(text_preview[:2000])


if __name__ == "__main__":
    sys.exit(main())
