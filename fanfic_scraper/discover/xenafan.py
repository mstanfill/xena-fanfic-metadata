from fanfic_scraper.fetch import XENAFAN, build_default_fetcher

TITLES_URL = "https://xenafan.com/fiction/titles.html"


def discover_xenafan(fetcher=None):
    """Fetches (or returns the cached copy of) the entire xenafan story index."""
    fetcher = fetcher or build_default_fetcher(XENAFAN)
    return fetcher.fetch(TITLES_URL)
