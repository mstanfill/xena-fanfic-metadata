from fanfic_scraper.fetch.cache import CacheStore
import pytest

from fanfic_scraper.fetch.client import Fetcher, PermanentFailure, RobotsDisallowed, RobotsUnavailable
from fanfic_scraper.fetch.config import SiteConfig
from fanfic_scraper.fetch.contact import MissingContactEmail
from fanfic_scraper.fetch.db import QueueDB
from fanfic_scraper.fetch.http_types import HttpResponse
from fanfic_scraper.fetch.politeness import Politeness

CONFIG = SiteConfig(name="test", host="example.test")


class RecordingPoliteness:
    """Politeness stub that records wait_for calls instead of sleeping."""

    def __init__(self, min_delay=5.0, max_delay=10.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.calls = []

    def wait_for(self, host, min_delay=None, max_delay=None):
        self.calls.append((host, min_delay, max_delay))
        return 0.0


def make_fetcher(tmp_path, http_get, **overrides):
    cache = CacheStore(tmp_path / "cache")
    db = QueueDB(tmp_path / "scrape.db")
    politeness = Politeness(
        min_delay=0.0, max_delay=0.0, sleep_fn=lambda s: None, clock_fn=lambda: 0.0,
    )
    kwargs = dict(
        config=CONFIG, cache=cache, db=db, politeness=politeness,
        http_get=http_get, contact_email="researcher@example.org", now_fn=lambda: "2026-10-20T00:00:00+00:00",
        sleep_fn=lambda s: None,
    )
    kwargs.update(overrides)
    return Fetcher(**kwargs)


def test_successful_fetch_writes_cache_and_marks_fetched(tmp_path):
    calls = []

    def http_get(url, headers):
        calls.append(url)
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        return HttpResponse(200, {"Content-Type": "text/html"}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    result = fetcher.fetch("https://example.test/page.html")

    assert result.status == 200
    assert result.body == b"<html>hi</html>"
    assert fetcher.db.get_status("https://example.test/page.html") == "fetched"


def test_second_fetch_is_served_from_cache_without_http_call(tmp_path):
    calls = []

    def http_get(url, headers):
        calls.append(url)
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    fetcher.fetch("https://example.test/page.html")
    calls.clear()
    result = fetcher.fetch("https://example.test/page.html")

    assert result.body == b"<html>hi</html>"
    assert calls == []  # no http_get calls at all on the cached path


def test_get_cached_never_calls_http(tmp_path):
    def http_get(url, headers):
        raise AssertionError("get_cached must not touch the network")

    fetcher = make_fetcher(tmp_path, http_get)
    assert fetcher.get_cached("https://example.test/page.html") is None


def test_crawl_delay_between_min_and_max_widens_window(tmp_path):
    # Default window is 5-10s; a Crawl-delay of 7 sits strictly inside it.
    # The bug being regression-tested: `crawl_delay > max_delay` never fires
    # for in-between values, so the window stayed (5, 10) and politeness
    # could legally draw a delay below the site's declared crawl-delay.
    politeness = RecordingPoliteness(min_delay=5.0, max_delay=10.0)

    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"User-agent: *\nCrawl-delay: 7\n")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get, politeness=politeness)
    fetcher.fetch("https://example.test/page.html")

    # First call is the robots.txt throttle (no override args), second is
    # the page fetch, which must use a window widened to respect the
    # 7-second crawl-delay: min raised to 7, max stays at 10.
    assert len(politeness.calls) == 2
    page_call = politeness.calls[1]
    assert page_call == ("example.test", 7.0, 10.0)


def test_robots_txt_fetch_is_politeness_throttled_before_page_fetch(tmp_path):
    # Bug being regression-tested: the robots.txt request bypassed
    # politeness entirely, so the real page request right after it could
    # fire with zero delay (no timestamp recorded for the host yet).
    politeness = RecordingPoliteness(min_delay=0.0, max_delay=0.0)

    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get, politeness=politeness)
    fetcher.fetch("https://example.test/page.html")

    # Exactly two wait_for calls: one before the robots.txt fetch, one
    # before the page fetch -- both throttled against the same host.
    assert len(politeness.calls) == 2
    assert politeness.calls[0][0] == "example.test"
    assert politeness.calls[1][0] == "example.test"


def test_robots_disallow_raises_and_marks_skipped(tmp_path):
    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"User-agent: *\nDisallow: /private/\n")
        raise AssertionError("should never fetch a disallowed URL")

    fetcher = make_fetcher(tmp_path, http_get)
    try:
        fetcher.fetch("https://example.test/private/secret.html")
        assert False, "expected RobotsDisallowed"
    except RobotsDisallowed:
        pass
    assert fetcher.db.get_status("https://example.test/private/secret.html") == "skipped_by_robots"


def test_retries_on_503_then_succeeds(tmp_path):
    attempts = {"n": 0}

    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        attempts["n"] += 1
        if attempts["n"] < 3:
            return HttpResponse(503, {}, None, b"")
        return HttpResponse(200, {}, "utf-8", b"<html>ok</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    result = fetcher.fetch("https://example.test/page.html")

    assert result.body == b"<html>ok</html>"
    assert attempts["n"] == 3


def test_permanent_failure_after_max_attempts_marks_failed(tmp_path):
    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        return HttpResponse(503, {}, None, b"")

    fetcher = make_fetcher(tmp_path, http_get, max_attempts=3)
    try:
        fetcher.fetch("https://example.test/page.html")
        assert False, "expected PermanentFailure"
    except PermanentFailure:
        pass
    assert fetcher.db.get_status("https://example.test/page.html") == "failed"


def test_subsequent_fetch_of_permanently_failed_url_raises_without_retrying(tmp_path):
    call_count = {"n": 0}

    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"")
        call_count["n"] += 1
        return HttpResponse(503, {}, None, b"")

    fetcher = make_fetcher(tmp_path, http_get, max_attempts=2)
    try:
        fetcher.fetch("https://example.test/page.html")
    except PermanentFailure:
        pass
    calls_on_first_pass = call_count["n"]

    try:
        fetcher.fetch("https://example.test/page.html")
        assert False, "expected PermanentFailure"
    except PermanentFailure:
        pass
    assert call_count["n"] == calls_on_first_pass  # no new HTTP attempts


def test_crawl_delay_widens_politeness_window(tmp_path):
    # Crawl-delay of 20 exceeds both the default min (5) and max (10), so
    # the widened window should raise both bounds to 20. This exercises a
    # different crawl_delay value than
    # test_crawl_delay_between_min_and_max_widens_window (7, which sits
    # strictly inside the default window) -- both regress distinct
    # comparison bugs in the same widening logic.
    #
    # Two recorded calls: `robots_for` throttles the robots.txt fetch with
    # the default window `(None, None)`, then the page fetch uses the
    # widened `(20.0, 20.0)`.
    seen_delays = []

    class RecordingPoliteness:
        min_delay = 0.0
        max_delay = 0.0

        def wait_for(self, host, min_delay=None, max_delay=None):
            seen_delays.append((min_delay, max_delay))
            return 0.0

    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(200, {}, "utf-8", b"User-agent: *\nCrawl-delay: 20\n")
        return HttpResponse(200, {}, "utf-8", b"<html></html>")

    fetcher = make_fetcher(tmp_path, http_get, politeness=RecordingPoliteness())
    fetcher.fetch("https://example.test/page.html")

    assert seen_delays == [(None, None), (20.0, 20.0)]


def test_unreachable_robots_txt_stops_without_fetching_page(tmp_path):
    calls = []

    def http_get(url, headers):
        calls.append(url)
        if url.endswith("robots.txt"):
            raise ConnectionError("proxy refused")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    with pytest.raises(RobotsUnavailable):
        fetcher.fetch("https://example.test/page.html")
    assert calls == ["https://example.test/robots.txt"]
    # Not marked failed, so a later run retries once robots.txt is reachable.
    assert fetcher.db.get_status("https://example.test/page.html") == "pending"


def test_robots_txt_server_error_stops_without_fetching_page(tmp_path):
    calls = []

    def http_get(url, headers):
        calls.append(url)
        if url.endswith("robots.txt"):
            return HttpResponse(503, {}, None, b"")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    with pytest.raises(RobotsUnavailable):
        fetcher.fetch("https://example.test/page.html")
    assert calls == ["https://example.test/robots.txt"]


def test_missing_robots_txt_404_allows_crawl(tmp_path):
    def http_get(url, headers):
        if url.endswith("robots.txt"):
            return HttpResponse(404, {}, None, b"Not Found")
        return HttpResponse(200, {}, "utf-8", b"<html>hi</html>")

    fetcher = make_fetcher(tmp_path, http_get)
    assert fetcher.fetch("https://example.test/page.html").status == 200


def test_extra_headers_sent_on_every_request(tmp_path):
    seen_headers = []

    def http_get(url, headers):
        seen_headers.append(dict(headers))
        return HttpResponse(200, {}, "utf-8", b"ok")

    config = SiteConfig(name="test", host="example.test", extra_headers={"Cookie": "X=1"})
    fetcher = make_fetcher(tmp_path, http_get, config=config)
    fetcher.fetch("https://example.test/page.html")

    assert len(seen_headers) == 2  # robots.txt, then the page
    assert all(h["Cookie"] == "X=1" for h in seen_headers)


def test_user_agent_carries_the_contact_email(tmp_path):
    seen = []

    def http_get(url, headers):
        seen.append(headers["User-Agent"])
        return HttpResponse(200, {}, "utf-8", b"")

    fetcher = make_fetcher(tmp_path, http_get)
    fetcher.fetch("https://example.test/page.html")
    assert seen == ["fanfic-metadata-research (researcher@example.org)"] * 2


def test_contact_email_is_only_asked_for_when_a_request_is_needed(tmp_path):
    asked = []

    def ask():
        asked.append(True)
        return "researcher@example.org"

    def http_get(url, headers):
        return HttpResponse(200, {}, "utf-8", b"page")

    fetcher = make_fetcher(tmp_path, http_get, contact_email=ask)
    fetcher.cache.write("https://example.test/saved.html", 200, {}, "utf-8", "t", b"saved")
    fetcher.fetch("https://example.test/saved.html")
    assert asked == []  # served from the cache, no prompt

    fetcher.fetch("https://example.test/page.html")
    fetcher.fetch("https://example.test/other.html")
    assert asked == [True]  # asked once, then reused


def test_missing_contact_email_stops_before_any_request(tmp_path):
    calls = []

    def http_get(url, headers):
        calls.append(url)
        return HttpResponse(200, {}, "utf-8", b"")

    fetcher = make_fetcher(tmp_path, http_get, contact_email="")
    with pytest.raises(MissingContactEmail):
        fetcher.fetch("https://example.test/page.html")
    assert calls == []
    assert fetcher.db.get_status("https://example.test/page.html") == "pending"
