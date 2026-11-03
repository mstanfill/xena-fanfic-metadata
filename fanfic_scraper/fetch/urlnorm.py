from urllib.parse import urlsplit, urlunsplit, unquote

from .config import SiteConfig


def normalize_url(raw_url: str, config: SiteConfig) -> tuple[str, str | None]:
    parts = urlsplit(raw_url)
    host = (parts.hostname or "").lower()
    if config.strip_www and host.startswith("www."):
        host = host[4:]
    path = unquote(parts.path)
    query = unquote(parts.query)
    fragment = parts.fragment or None
    normalized = urlunsplit((config.scheme, host, path, query, ""))
    return normalized, fragment
