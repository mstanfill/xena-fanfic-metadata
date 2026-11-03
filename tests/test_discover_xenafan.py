from fanfic_scraper.discover.xenafan import TITLES_URL, discover_xenafan


class StubFetcher:
    def __init__(self, response):
        self.response = response
        self.requested_urls = []

    def fetch(self, url):
        self.requested_urls.append(url)
        return self.response


def test_discover_xenafan_fetches_the_titles_index():
    stub = StubFetcher(response="the-cached-response")
    result = discover_xenafan(fetcher=stub)
    assert stub.requested_urls == [TITLES_URL]
    assert result == "the-cached-response"


def test_titles_url_is_the_documented_entry_point():
    assert TITLES_URL == "https://xenafan.com/fiction/titles.html"
