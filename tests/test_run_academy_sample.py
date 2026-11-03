from fanfic_scraper.discover.academy import AUTHORS_INDEX_URL, discover_academy
from fanfic_scraper.scripts.run_academy_sample import (
    build_display_names_by_normalized_url,
    lookup_display_names,
)

FIXTURE = b"""<html><body>
<p><a href="http://www.academyofbards.org/authors/tidewriter.html">* Tidewriter</a></p>
</body></html>
"""


class StubFetcher:
    def __init__(self, pages_by_url):
        self.pages_by_url = pages_by_url

    def fetch(self, url):
        return self.pages_by_url[url]


class FakeIndexPage:
    def __init__(self, body):
        self.body = body


class FakeCachedPage:
    """Mimics the relevant shape of fetch.cache.CachedResponse: a `.url`
    that the fetcher has already normalized to the site's configured
    scheme, which can differ from the raw scheme stored on the index
    entry (entries keep whatever scheme the index itself used)."""

    def __init__(self, url, body=b"<html></html>"):
        self.url = url
        self.body = body


def test_discover_then_runner_lookup_matches_despite_scheme_difference():
    # The raw index entry URL uses http (stored as-is). The fetcher's
    # cached response normalizes the URL to the site's configured scheme
    # (https for ACADEMY) before handing it back to callers -- this is the
    # exact discrepancy that silently broke author-name matching in the
    # sample runner (every record ended up with authors == []).
    raw_entry_url = "http://www.academyofbards.org/authors/tidewriter.html"
    normalized_page_url = "https://www.academyofbards.org/authors/tidewriter.html"

    stub = StubFetcher({
        AUTHORS_INDEX_URL: FakeIndexPage(FIXTURE),
        raw_entry_url: FakeCachedPage(normalized_page_url),
    })

    _, entries, sample_pages = discover_academy(fetcher=stub, sample_urls=[raw_entry_url])

    by_url = build_display_names_by_normalized_url(entries)
    page = sample_pages[0]

    assert page.url != raw_entry_url  # sanity check the scheme really differs
    assert lookup_display_names(by_url, page.url) == ["Tidewriter"]
