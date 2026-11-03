from fanfic_scraper.discover.athenaeum import (
    BASE_SEARCH_URL, _total_found_from_html, build_page_urls, discover_athenaeum,
)


def test_total_found_from_html_reads_the_query_param():
    body = b'...href="athenaeum_search_v1.cfm?...&start_row=51&total_found=6966&...'
    assert _total_found_from_html(body) == 6966


def test_build_page_urls_page_one_is_the_bare_search_url():
    urls = build_page_urls(total_found=120, max_pages=1)
    assert urls == [BASE_SEARCH_URL]


def test_build_page_urls_covers_a_short_final_page():
    # 6966 / 50 = 139.32 -> 140 pages; the last one is not skipped or padded.
    urls = build_page_urls(total_found=6966)
    assert len(urls) == 140
    assert "start_row=6951" in urls[-1]
    assert "total_found=6966" in urls[-1]
    assert "page_displayed=140" in urls[-1]


def test_build_page_urls_respects_max_pages_cap():
    urls = build_page_urls(total_found=6966, max_pages=2)
    assert len(urls) == 2
    assert urls[0] == BASE_SEARCH_URL
    assert "start_row=51" in urls[1]


class StubFetcher:
    def __init__(self):
        self.requested_urls = []

    def fetch(self, url):
        self.requested_urls.append(url)
        return FakePage(b"...total_found=120...")


class FakePage:
    def __init__(self, body):
        self.body = body


def test_discover_athenaeum_fetches_page_one_then_the_rest():
    stub = StubFetcher()
    result = discover_athenaeum(fetcher=stub, max_pages=3)

    assert len(result) == 3
    assert stub.requested_urls[0] == BASE_SEARCH_URL
    assert "start_row=51" in stub.requested_urls[1]
    assert "start_row=101" in stub.requested_urls[2]
