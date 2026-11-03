from dataclasses import dataclass, field


@dataclass
class Part:
    label: str
    url: str | None = None


@dataclass
class Record:
    source_site: str
    source_id: str
    title: str
    title_normalized: str = ""
    authors: list = field(default_factory=list)
    author_page_url: str | None = None
    parts: list = field(default_factory=list)  # list[Part]
    work_type: str | None = None
    series: str | None = None
    series_members: list = field(default_factory=list)
    summary: str | None = None
    status: str | None = None
    universe: str | None = None
    era: str | None = None
    orientation: str | None = None
    genre: str | None = None
    length_pages: int | None = None
    date: str | None = None
    cast: str | None = None
    related_episodes: str | None = None
    awards: str | None = None
    ratings: dict | None = None
    ebook_available: bool = False
    ebook_links: list = field(default_factory=list)
    disclaimer_text: str | None = None
    external_url: str | None = None
    notes: str | None = None
    fetched_from: list = field(default_factory=list)
