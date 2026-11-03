from fanfic_scraper.fetch.config import XENAFAN
from fanfic_scraper.fetch.urlnorm import normalize_url


def test_strips_www_and_forces_scheme():
    url, frag = normalize_url("http://www.xenafan.com/fiction/titles.html", XENAFAN)
    assert url == "https://xenafan.com/fiction/titles.html"
    assert frag is None


def test_lowercases_host_but_not_path():
    url, _ = normalize_url("https://XenaFan.com/Fiction/Titles.html", XENAFAN)
    assert url == "https://xenafan.com/Fiction/Titles.html"


def test_decodes_percent_20():
    url, _ = normalize_url("https://xenafan.com/fiction/my%20story.html", XENAFAN)
    assert url == "https://xenafan.com/fiction/my story.html"


def test_splits_off_meaningful_fragment():
    url, frag = normalize_url(
        "https://xenafan.com/fiction/list/storylinks.html#somebard", XENAFAN
    )
    assert url == "https://xenafan.com/fiction/list/storylinks.html"
    assert frag == "somebard"


def test_no_fragment_returns_none():
    url, frag = normalize_url("https://xenafan.com/fiction/titles.html", XENAFAN)
    assert frag is None


def test_decodes_percent_20_in_query_string_too():
    url, _ = normalize_url(
        "https://xenafan.com/fiction/search.html?q=xena%20gabrielle", XENAFAN
    )
    assert url == "https://xenafan.com/fiction/search.html?q=xena gabrielle"
