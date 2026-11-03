import hashlib
import json
import pathlib
from dataclasses import dataclass


@dataclass
class CachedResponse:
    url: str
    status: int
    headers: dict
    charset: str | None
    fetched_at: str
    body: bytes


class CacheStore:
    def __init__(self, cache_dir):
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, normalized_url: str) -> str:
        return hashlib.sha1(normalized_url.encode("utf-8")).hexdigest()

    def _paths(self, normalized_url: str):
        key = self._key(normalized_url)
        return self.cache_dir / key, self.cache_dir / f"{key}.meta.json"

    def read(self, normalized_url: str) -> CachedResponse | None:
        body_path, meta_path = self._paths(normalized_url)
        if not body_path.exists() or not meta_path.exists():
            return None
        meta = json.loads(meta_path.read_text("utf-8"))
        return CachedResponse(
            url=meta["url"],
            status=meta["status"],
            headers=meta["headers"],
            charset=meta.get("charset"),
            fetched_at=meta["fetched_at"],
            body=body_path.read_bytes(),
        )

    def write(self, normalized_url, status, headers, charset, fetched_at, body) -> CachedResponse:
        body_path, meta_path = self._paths(normalized_url)
        body_path.write_bytes(body)
        meta_path.write_text(
            json.dumps(
                {
                    "url": normalized_url,
                    "status": status,
                    "headers": headers,
                    "charset": charset,
                    "fetched_at": fetched_at,
                }
            ),
            encoding="utf-8",
        )
        return self.read(normalized_url)
