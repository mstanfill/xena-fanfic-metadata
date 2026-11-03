from fanfic_scraper.discover.academy import AUTHORS_INDEX_URL, parse_author_index, discover_academy

# Invented author index that reproduces the real index's quirks: two
# aliases for one page, a link without .html, a %20 link, and a link
# outside /authors/. No real author names.
FIXTURE = b"""<html><body>
<p><a href="http://www.academyofbards.org/authors/lantern.html">* Lantern (aka Jo Example)</a></p>
<p><a href="http://www.academyofbards.org/authors/ab_smith.html">* Smith, AB</a></p>
<p><a href="http://www.academyofbards.org/authors/lantern.html">* Example, Jo (aka Lantern)</a></p>
<p><a href="http://www.academyofbards.org/authors/tidewriter.html">* Tidewriter</a></p>
<p><a href="http://www.academyofbards.org/authors/pat_sample">* Pat Sample</a></p>
<p><a href="http://www.academyofbards.org/authors/kim%20ex.html">* Kim Ex</a></p>
<p><a href="http://www.academyofbards.org/amazontrails/xena/altfict.htm#wanderer">* Wanderer</a></p>
</body></html>
"""


def test_authors_index_url_is_the_documented_entry_point():
    assert AUTHORS_INDEX_URL == "https://www.academyofbards.org/authors/"


def test_aliases_for_the_same_url_are_aggregated_not_collapsed():
    entries = parse_author_index(FIXTURE)
    lantern = next(e for e in entries if e.url.endswith("/authors/lantern.html"))
    assert set(lantern.display_names) == {"Lantern (aka Jo Example)", "Example, Jo (aka Lantern)"}


def test_bullet_prefix_is_stripped():
    entries = parse_author_index(FIXTURE)
    tide = next(e for e in entries if e.url.endswith("/authors/tidewriter.html"))
    assert tide.display_names == ["Tidewriter"]


def test_links_without_html_percent_encoding_and_outside_authors_are_kept_as_is():
    entries = parse_author_index(FIXTURE)
    urls = {e.url for e in entries}
    assert "http://www.academyofbards.org/authors/pat_sample" in urls
    assert "http://www.academyofbards.org/authors/kim%20ex.html" in urls
    assert "http://www.academyofbards.org/amazontrails/xena/altfict.htm#wanderer" in urls


class StubFetcher:
    def __init__(self, pages_by_url):
        self.pages_by_url = pages_by_url
        self.requested_urls = []

    def fetch(self, url):
        self.requested_urls.append(url)
        return self.pages_by_url[url]


class FakePage:
    def __init__(self, body):
        self.body = body


def test_discover_academy_fetches_index_then_the_given_sample_urls():
    index_page = FakePage(FIXTURE)
    sample_urls = ["http://www.academyofbards.org/authors/tidewriter.html"]
    stub = StubFetcher({AUTHORS_INDEX_URL: index_page, sample_urls[0]: FakePage(b"<html></html>")})

    index_page_result, entries, sample_pages = discover_academy(fetcher=stub, sample_urls=sample_urls)

    assert index_page_result is index_page
    assert len(entries) == 6  # 7 <p> lines, lantern.html counted once -> 6 unique URLs
    assert stub.requested_urls == [AUTHORS_INDEX_URL] + sample_urls
    assert len(sample_pages) == 1
