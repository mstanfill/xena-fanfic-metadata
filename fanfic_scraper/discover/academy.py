from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from fanfic_scraper.fetch import ACADEMY, build_default_fetcher

AUTHORS_INDEX_URL = "https://www.academyofbards.org/authors/"

# Chosen to cover the markup variety seen on real author pages: a series
# grouping + many-part story (cruise), a co-author + bracket-tag + ebook-icon
# + alias-collision page (advocate), an ordinary .html author page
# (lynn_ames), a %20 link, and one more picked for alphabetical spread.
SAMPLE_AUTHOR_URLS = [
    "http://www.academyofbards.org/authors/cruise.html",
    "http://www.academyofbards.org/authors/advocate.html",
    "http://www.academyofbards.org/authors/lynn_ames.html",
    "http://www.academyofbards.org/authors/caitlin%20mcewen.html",
    "http://www.academyofbards.org/authors/nene_adams.html",
]


@dataclass
class AuthorEntry:
    url: str
    display_names: list = field(default_factory=list)


def parse_author_index(html_bytes: bytes) -> list:
    soup = BeautifulSoup(html_bytes, "lxml")
    by_url = {}
    order = []
    for a in soup.find_all("a", href=True):
        url = urljoin(AUTHORS_INDEX_URL, a["href"])
        name = a.get_text(strip=True)
        if name.startswith("* "):
            name = name[2:]
        if url not in by_url:
            by_url[url] = AuthorEntry(url=url, display_names=[])
            order.append(url)
        by_url[url].display_names.append(name)
    return [by_url[url] for url in order]


def discover_academy(fetcher=None, sample_urls=None) -> tuple:
    fetcher = fetcher or build_default_fetcher(ACADEMY)
    sample_urls = sample_urls if sample_urls is not None else SAMPLE_AUTHOR_URLS
    index_page = fetcher.fetch(AUTHORS_INDEX_URL)
    entries = parse_author_index(index_page.body)
    sample_pages = [fetcher.fetch(url) for url in sample_urls]
    return index_page, entries, sample_pages
