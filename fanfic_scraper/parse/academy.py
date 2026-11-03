import re
from urllib.parse import urljoin

import ftfy
from bs4 import BeautifulSoup

from .schema import Part, Record

SOURCE_SITE = "academy"
_UPDATE_DATE_RE = re.compile(r"Last Updated:\s*(.+)")
_WORK_TYPES = {"poem", "screenplay", "song", "songs", "lyric", "lyrics"}


def _clean(text: str) -> str:
    return ftfy.fix_text(re.sub(r"\s+", " ", text).strip())


def last_updated_date(html_bytes: bytes) -> str | None:
    """The real "Last Updated:" value -- the first id="update" paragraph
    whose text actually matches, skipping any other id="update" block
    (e.g. Hall-of-Fame/achievement text) that doesn't."""
    soup = BeautifulSoup(html_bytes, "lxml")
    for el in soup.find_all("p", id="update"):
        match = _UPDATE_DATE_RE.search(el.get_text(" ", strip=True))
        if match:
            return match.group(1).strip()
    return None


def parse_author_page(html_bytes: bytes, page_url: str, display_names: list) -> list:
    soup = BeautifulSoup(html_bytes, "lxml")
    records = []
    title_ps = []
    title_p, parts_els, contence_el = None, [], None
    for el in soup.find_all(["p"], id=["title", "contence", "parts"]):
        if el.get("id") == "title":
            if title_p is not None:
                records.append(_build_record(title_p, parts_els, contence_el, page_url, display_names))
                title_ps.append(title_p)
            title_p, parts_els, contence_el = el, [], None
        elif el.get("id") == "contence" and title_p is not None and contence_el is None:
            contence_el = el
        elif el.get("id") == "parts" and title_p is not None:
            parts_els.append(el)
    if title_p is not None:
        records.append(_build_record(title_p, parts_els, contence_el, page_url, display_names))
        title_ps.append(title_p)
    _apply_series_grouping(soup, records, title_ps)
    return records


def _apply_series_grouping(soup, records: list, title_ps: list) -> None:
    """Records whose <p id="title"> lives inside a top-level <div id="inset">
    belong to the series named by that div's preceding <p id="series">
    sibling. Tag each such record's .series and .series_members (every other
    record in the same group, excluding itself)."""
    for inset in soup.find_all("div", id="inset"):
        series_p = inset.find_previous_sibling("p", id="series")
        if series_p is None:
            continue
        series_name = _clean(series_p.get_text())
        group = [r for r, title_p in zip(records, title_ps) if inset in title_p.parents]
        for r in group:
            r.series = series_name
            r.series_members = [Part(label=other.title, url=other.source_id) for other in group if other is not r]


def _build_record(title_p, parts_els, contence_el, page_url, display_names) -> Record:
    link = title_p.find("a")
    title = _clean(link.get_text())
    href = urljoin(page_url, link["href"])

    with_span = title_p.find("span", id="with")
    incomplete_span = title_p.find("span", id="incomplete")
    note_span = title_p.find("span", id="note")
    ebook_available = title_p.find("img", id="ebook") is not None

    work_type, status, notes_parts = None, None, []
    if incomplete_span is not None:
        status = "incomplete"
    if note_span is not None:
        tag_text = note_span.get_text(strip=True).strip("[]")
        if tag_text.lower() in _WORK_TYPES:
            work_type = tag_text.lower()
        else:
            notes_parts.append(tag_text)
    if with_span is not None:
        notes_parts.append(_clean(with_span.get_text(strip=True)).lstrip("-").strip())

    parts = []
    for parts_el in parts_els:
        for a in parts_el.find_all("a"):
            parts.append(Part(label=_clean(a.get_text()), url=urljoin(page_url, a["href"])))
    if not parts:
        parts = [Part(label="Part 1", url=href)]

    summary = _clean(contence_el.get_text()) if contence_el is not None else None

    return Record(
        source_site=SOURCE_SITE,
        source_id=href,
        title=title,
        authors=list(display_names),
        author_page_url=page_url,
        parts=parts,
        work_type=work_type,
        summary=summary,
        status=status,
        notes="; ".join(notes_parts) or None,
        ebook_available=ebook_available,
        fetched_from=[page_url],
    )
