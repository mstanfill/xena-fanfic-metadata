import os
import pathlib

from .cache import CacheStore, CachedResponse
from .client import Fetcher, FetchError, PermanentFailure, RobotsDisallowed, RobotsUnavailable
from .config import ACADEMY, AGENT_NAME, ATHENAEUM, SiteConfig, XENAFAN, user_agent_for
from .contact import MissingContactEmail, resolve_contact_email, validate_contact_email
from .db import QueueDB
from .http_requests import requests_http_get
from .http_types import HttpResponse
from .politeness import Politeness
from .robots import RobotsRules, parse_robots

DATA_DIR_ENV_VAR = "FANFIC_DATA_DIR"


def default_data_dir() -> pathlib.Path:
    """FANFIC_DATA_DIR if set, else ./data relative to the current directory."""
    return pathlib.Path(os.environ.get(DATA_DIR_ENV_VAR, "data"))


def build_default_fetcher(config: SiteConfig, data_dir=None, contact_email=None) -> Fetcher:
    """A Fetcher with the disk cache and queue under `data_dir`.

    `contact_email` may be omitted: it is then resolved (environment variable
    or prompt) only when the first network request is about to be sent.
    """
    data_dir = pathlib.Path(data_dir) if data_dir is not None else default_data_dir()
    cache = CacheStore(data_dir / "cache")
    db = QueueDB(data_dir / "scrape.db")
    politeness = Politeness(min_delay=config.min_delay, max_delay=config.max_delay)
    return Fetcher(config, cache, db, politeness, requests_http_get,
                   contact_email=contact_email or resolve_contact_email)


__all__ = [
    "SiteConfig", "XENAFAN", "ATHENAEUM", "ACADEMY", "AGENT_NAME", "user_agent_for",
    "HttpResponse", "requests_http_get", "CacheStore", "CachedResponse", "QueueDB",
    "RobotsRules", "parse_robots", "Politeness", "Fetcher", "FetchError", "PermanentFailure",
    "RobotsDisallowed", "RobotsUnavailable", "MissingContactEmail", "resolve_contact_email",
    "validate_contact_email", "DATA_DIR_ENV_VAR", "default_data_dir", "build_default_fetcher",
]
