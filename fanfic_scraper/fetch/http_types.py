from dataclasses import dataclass


@dataclass
class HttpResponse:
    status: int
    headers: dict
    charset: str | None
    body: bytes
