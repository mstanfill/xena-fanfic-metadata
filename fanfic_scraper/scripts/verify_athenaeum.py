"""Live check for the Athenaeum (xenafiction.net): robots.txt and search
results pages 1-2.

Makes 3 requests through the project fetcher, so the politeness, robots and
cache rules apply. The search pages are saved to the data folder; re-running
reads them from the saved copies, and only robots.txt is requested again.

    fanfic-verify-athenaeum          (or: python -m fanfic_scraper.scripts.verify_athenaeum)
"""
import sys

from fanfic_scraper.discover.athenaeum import _total_found_from_html, discover_athenaeum
from fanfic_scraper.fetch import ATHENAEUM, build_default_fetcher


def main():
    fetcher = build_default_fetcher(ATHENAEUM)

    robots = fetcher.robots_for(ATHENAEUM.host)
    print(f"robots.txt for {ATHENAEUM.host}:")
    print(f"  disallow_prefixes = {robots.disallow_prefixes}")
    print(f"  crawl_delay       = {robots.crawl_delay}")
    print()

    pages = discover_athenaeum(fetcher, max_pages=2)
    total_found = _total_found_from_html(pages[0].body)
    print(f"total_found = {total_found} (6966 when last checked)")
    for i, page in enumerate(pages, 1):
        body_text = page.body.decode(page.charset or "utf-8", errors="replace")
        print(f"page {i}: status={page.status} bytes={len(page.body)} "
              f"reader_recommendation_blocks={body_text.count('Reader Recommendation')}")
    print()
    text_preview = pages[0].body.decode(pages[0].charset or "utf-8", errors="replace")
    idx = text_preview.find('id="title"')
    print("Markup around the first record's title block:")
    print(text_preview[max(0, idx - 200): idx + 1200])


if __name__ == "__main__":
    sys.exit(main())
