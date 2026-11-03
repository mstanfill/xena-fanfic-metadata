import math
import re

from fanfic_scraper.fetch import ATHENAEUM, build_default_fetcher

_SEARCH_PATH = "http://xenafiction.net/styles/athenaeum_deepblue/athenaeum_search_v1.cfm"
BASE_SEARCH_URL = (
    f"{_SEARCH_PATH}?page_type=search&keyword_search=&search_by=TITLE"
    "&GENRE=Any&PAGES=Any&UNIVERSE=Any&EBOOK_FLAG=&ERA=Any&AUDIENCE=Any"
    "&LANGUAGE=&FOCUS=None"
)
_PAGE_SIZE = 50
_TOTAL_FOUND_RE = re.compile(r"total_found=(\d+)")


def _total_found_from_html(body: bytes) -> int:
    text = body.decode("utf-8", errors="replace")
    return int(_TOTAL_FOUND_RE.search(text).group(1))


def build_page_urls(total_found: int, max_pages: int = None) -> list:
    total_pages = math.ceil(total_found / _PAGE_SIZE)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)
    urls = [BASE_SEARCH_URL]
    for page in range(2, total_pages + 1):
        start_row = (page - 1) * _PAGE_SIZE + 1
        urls.append(
            f"{_SEARCH_PATH}?keyword_search=&UNIVERSE=Any&ERA=Any&AUDIENCE=Any"
            f"&GENRE=Any&PAGES=Any&FOCUS=None&REVIEW=&EBOOK_FLAG="
            f"&start_row={start_row}&total_found={total_found}"
            f"&search_by=TITLE&page_displayed={page}"
        )
    return urls


def discover_athenaeum(fetcher=None, max_pages=None) -> list:
    """Fetches (or returns the cached copies of) the Athenaeum search-results
    pages, up to `max_pages` (None = all ~140 pages)."""
    fetcher = fetcher or build_default_fetcher(ATHENAEUM)
    page_one = fetcher.fetch(BASE_SEARCH_URL)
    total_found = _total_found_from_html(page_one.body)
    urls = build_page_urls(total_found, max_pages)
    return [page_one] + [fetcher.fetch(url) for url in urls[1:]]
