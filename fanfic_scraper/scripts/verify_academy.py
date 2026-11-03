"""Live check for the Academy of Bards: robots.txt, the author index, and
5 author pages chosen for their markup variety.

Makes 7 requests through the project fetcher, so the politeness, robots and
cache rules apply. Pages are saved to the data folder; re-running reads them
from the saved copies, and only robots.txt is requested again.

    fanfic-verify-academy            (or: python -m fanfic_scraper.scripts.verify_academy)
"""
import sys

from fanfic_scraper.discover.academy import discover_academy
from fanfic_scraper.fetch import ACADEMY, build_default_fetcher


def main():
    fetcher = build_default_fetcher(ACADEMY)

    robots = fetcher.robots_for(ACADEMY.host)
    print(f"robots.txt for {ACADEMY.host}:")
    print(f"  disallow_prefixes = {robots.disallow_prefixes}")
    print(f"  crawl_delay       = {robots.crawl_delay}")
    print()

    index_page, entries, sample_pages = discover_academy(fetcher)
    print(f"{len(entries)} unique author URLs found in the index")
    for page in sample_pages:
        print(f"  {page.url}: status={page.status} bytes={len(page.body)}")


if __name__ == "__main__":
    sys.exit(main())
