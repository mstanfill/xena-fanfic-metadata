from fanfic_scraper.fetch.cache import CacheStore


def test_read_missing_returns_none(tmp_path):
    store = CacheStore(tmp_path / "cache")
    assert store.read("https://xenafan.com/fiction/titles.html") is None


def test_write_then_read_roundtrip(tmp_path):
    store = CacheStore(tmp_path / "cache")
    url = "https://xenafan.com/fiction/titles.html"
    store.write(url, 200, {"Content-Type": "text/html"}, "utf-8", "2026-10-20T00:00:00+00:00", b"<html></html>")
    cached = store.read(url)
    assert cached is not None
    assert cached.url == url
    assert cached.status == 200
    assert cached.headers == {"Content-Type": "text/html"}
    assert cached.charset == "utf-8"
    assert cached.body == b"<html></html>"


def test_different_urls_get_different_keys(tmp_path):
    store = CacheStore(tmp_path / "cache")
    store.write("https://xenafan.com/a.html", 200, {}, None, "t", b"A")
    store.write("https://xenafan.com/b.html", 200, {}, None, "t", b"B")
    assert store.read("https://xenafan.com/a.html").body == b"A"
    assert store.read("https://xenafan.com/b.html").body == b"B"
