from fanfic_scraper.fetch.http_requests import requests_http_get


def test_requests_http_get_wraps_response(requests_mock):
    requests_mock.get(
        "https://example.test/page.html",
        status_code=200,
        headers={"Content-Type": "text/html; charset=utf-8"},
        content=b"<html>hi</html>",
    )
    resp = requests_http_get("https://example.test/page.html", {"User-Agent": "test-agent"})
    assert resp.status == 200
    assert resp.body == b"<html>hi</html>"
    assert "text/html" in resp.headers["Content-Type"]


def test_sends_the_given_user_agent_header(requests_mock):
    requests_mock.get("https://example.test/page.html", status_code=200, content=b"ok")
    requests_http_get("https://example.test/page.html", {"User-Agent": "fanfic-metadata-research (researcher@example.org)"})
    sent_headers = requests_mock.last_request.headers
    assert sent_headers["User-Agent"] == "fanfic-metadata-research (researcher@example.org)"
