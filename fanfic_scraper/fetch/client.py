import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .config import AGENT_NAME, user_agent_for
from .contact import validate_contact_email
from .robots import parse_robots
from .urlnorm import normalize_url


class FetchError(Exception):
    pass


class PermanentFailure(FetchError):
    pass


class RobotsDisallowed(FetchError):
    pass


class RobotsUnavailable(FetchError):
    pass


class Fetcher:
    def __init__(self, config, cache, db, politeness, http_get, contact_email,
                 max_attempts=5, backoff_base=2.0, now_fn=None, sleep_fn=time.sleep):
        self.config = config
        self.cache = cache
        self.db = db
        self.politeness = politeness
        self.http_get = http_get
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.now_fn = now_fn or (lambda: datetime.now(timezone.utc).isoformat())
        self.sleep_fn = sleep_fn
        # A string, or a zero-argument callable (e.g. a prompt) that is only
        # called when the first network request is about to be sent.
        self._contact_email = contact_email
        self._user_agent = None
        self._robots_cache = {}

    def get_cached(self, raw_url: str):
        normalized_url, _fragment = normalize_url(raw_url, self.config)
        return self.cache.read(normalized_url)

    def _headers(self) -> dict:
        if self._user_agent is None:
            email = self._contact_email() if callable(self._contact_email) else self._contact_email
            self._user_agent = user_agent_for(validate_contact_email(email))
        return {"User-Agent": self._user_agent, **self.config.extra_headers}

    def robots_for(self, host: str):
        if host not in self._robots_cache:
            headers = self._headers()  # resolve the contact email before any request
            self.politeness.wait_for(host)
            robots_url = f"{self.config.scheme}://{host}/robots.txt"
            try:
                resp = self.http_get(robots_url, headers)
            except Exception as exc:
                raise RobotsUnavailable(
                    f"robots.txt for {host} could not be fetched ({exc}); not crawling"
                ) from exc
            # RFC 9309: a 4xx means there is no robots.txt (crawl allowed);
            # a 5xx or unreachable host means assume everything is disallowed.
            if resp.status == 200:
                text = resp.body.decode("utf-8", errors="replace")
            elif 400 <= resp.status < 500:
                text = ""
            else:
                raise RobotsUnavailable(
                    f"robots.txt for {host} returned HTTP {resp.status}; not crawling"
                )
            self._robots_cache[host] = parse_robots(text, AGENT_NAME)
        return self._robots_cache[host]

    def fetch(self, raw_url: str):
        normalized_url, _fragment = normalize_url(raw_url, self.config)
        cached = self.cache.read(normalized_url)
        if cached is not None:
            return cached

        self.db.enqueue(normalized_url, self.config.host)
        if self.db.get_status(normalized_url) == "failed":
            raise PermanentFailure(f"{normalized_url} previously failed permanently")

        robots = self.robots_for(self.config.host)
        path = urlsplit(normalized_url).path or "/"
        if not robots.is_allowed(path):
            self.db.mark_skipped_by_robots(normalized_url, self.now_fn())
            raise RobotsDisallowed(f"{normalized_url} disallowed by robots.txt")

        min_delay, max_delay = self.politeness.min_delay, self.politeness.max_delay
        if robots.crawl_delay is not None:
            min_delay = max(min_delay, robots.crawl_delay)
            max_delay = max(max_delay, robots.crawl_delay)

        headers = self._headers()
        last_error = None
        for attempt in range(1, self.max_attempts + 1):
            self.politeness.wait_for(self.config.host, min_delay, max_delay)
            try:
                resp = self.http_get(normalized_url, headers)
            except Exception as exc:
                last_error = str(exc)
                self.sleep_fn(self.backoff_base ** attempt)
                continue
            if resp.status in (429, 503) or resp.status >= 500:
                last_error = f"HTTP {resp.status}"
                self.sleep_fn(self.backoff_base ** attempt)
                continue
            cached = self.cache.write(
                normalized_url, resp.status, resp.headers, resp.charset, self.now_fn(), resp.body
            )
            self.db.mark_fetched(normalized_url, self.now_fn())
            return cached

        self.db.mark_failed(normalized_url, last_error or "unknown error", self.now_fn())
        raise PermanentFailure(
            f"{normalized_url} failed after {self.max_attempts} attempts: {last_error}"
        )
