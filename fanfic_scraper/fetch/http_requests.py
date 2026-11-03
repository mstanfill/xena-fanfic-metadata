import requests

from .http_types import HttpResponse


def requests_http_get(url: str, headers: dict, timeout: float = 15.0) -> HttpResponse:
    resp = requests.get(url, headers=headers, timeout=timeout)
    return HttpResponse(
        status=resp.status_code,
        headers=dict(resp.headers),
        charset=resp.encoding,
        body=resp.content,
    )
