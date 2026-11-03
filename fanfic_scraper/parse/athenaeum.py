import re
from urllib.parse import urljoin

import ftfy
from bs4 import BeautifulSoup

from .schema import Part, Record

SOURCE_SITE = "athenaeum"
_I_KEY_RE = re.compile(r"I_KEY=(\d+)")
_REDIR_RE = re.compile(r"redir\.cfm\?sn=\d+&ex_site=(.+)$")
_RECORD_SPLIT_RE = re.compile(
    r'(?=<A href="comments\.cfm\?I_KEY=\d+&command=enter"\s+class="comments")', re.IGNORECASE
)

# Confirmed from the real advanced-search form (2026-10-25); extend
# _KNOWN_ORIENTATIONS if later live pages reveal values beyond "Alternative".
_KNOWN_ERAS = {"Ancient", "Middle Ages", "Pre-1900", "1900-1960", "Modern", "Futuristic"}
_KNOWN_GENRES = {"Adventure", "Drama", "Horror", "Humor", "Mystery",
                  "Romance (alt)", "Romance", "Vignette", "Poetry"}
_KNOWN_ORIENTATIONS = {"Alternative"}
_KNOWN_STATUSES = {"Finished", "Unfinished"}
_LENGTH_RE = re.compile(r".*-\s*(\d+)\s*pages", re.IGNORECASE)
_DATE_RE = re.compile(r"^[A-Za-z]{3}-\d{2}$")
_RATINGS_RE = re.compile(
    r"Overall:\s*([\d.]+)\s*\(Rated (\d+) times?\).*?"
    r"Spice Index:\s*([\d.]+)\s*\(Rated (\d+) times?\)",
    re.DOTALL,
)
_AUTHOR_SPLIT_RE = re.compile(r"\s*&\s*|\s+and\s+", re.IGNORECASE)
_CHARSET_RE = re.compile(r'charset\s*=\s*["\']?\s*([\w-]+)', re.IGNORECASE)


def _decode(html_bytes: bytes) -> str:
    """Decode raw bytes, preferring a declared <meta charset>, then UTF-8,
    then cp1252/latin-1 as last-resort fallbacks (the Athenaeum serves a mix
    of encodings, often mislabeled)."""
    head = html_bytes[:4096].decode("ascii", errors="ignore")
    match = _CHARSET_RE.search(head)
    candidates = []
    if match:
        candidates.append(match.group(1))
    for enc in ("utf-8", "cp1252", "latin-1"):
        if enc not in candidates:
            candidates.append(enc)
    for enc in candidates:
        try:
            return html_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return html_bytes.decode("utf-8", errors="replace")


def _clean(text: str) -> str:
    """Normalize whitespace and repair any mojibake via ftfy."""
    collapsed = re.sub(r"\s+", " ", text).strip()
    return ftfy.fix_text(collapsed)


def _split_authors(text: str) -> list:
    return [_clean(a) for a in _AUTHOR_SPLIT_RE.split(text) if a.strip()]


def _parse_pipe_line(text: str) -> dict:
    fields = {"universe": None, "era": None, "orientation": None, "genre": None,
              "length_pages": None, "status": None, "date": None}
    segments = [s.strip() for s in text.split("|") if s.strip()]
    if not segments:
        return fields
    fields["universe"] = segments[0]  # Universe is always first and never missing.
    for segment in segments[1:]:
        length_match = _LENGTH_RE.match(segment)
        if length_match:
            fields["length_pages"] = int(length_match.group(1))
        elif segment in _KNOWN_STATUSES:
            fields["status"] = segment
        elif segment in _KNOWN_ERAS:
            fields["era"] = segment
        elif segment in _KNOWN_GENRES:
            fields["genre"] = segment
        elif segment in _KNOWN_ORIENTATIONS:
            fields["orientation"] = segment
        elif _DATE_RE.match(segment):
            fields["date"] = segment
    return fields


def parse_athenaeum_search_page(html_bytes: bytes, page_url: str) -> list:
    text = _decode(html_bytes)
    chunks = _RECORD_SPLIT_RE.split(text)[1:]  # [0] is header/pagination before any record
    records = []
    for chunk in chunks:
        record = _parse_record_chunk(chunk, page_url)
        if record is not None:
            records.append(record)
    return records


def _after_label(text: str) -> str:
    """Strips a leading "Label:" prefix from a div's joined text."""
    return text.split(":", 1)[1].strip() if ":" in text else text.strip()


def _parse_record_chunk(chunk: str, page_url: str):
    i_key_match = _I_KEY_RE.search(chunk)
    soup = BeautifulSoup(chunk, "lxml")
    title_div = soup.find("div", id="title")
    if i_key_match is None or title_div is None:
        return None
    source_id = i_key_match.group(1)

    title_link = title_div.find("a", class_="title")
    no_title_span = title_div.find("span", class_="no_title")
    author_link = title_div.find("a", class_="author")

    title, external_url, parts, status_from_title_block = None, None, [], None
    if title_link is not None:
        href = title_link.get("href", "")
        title = _clean(title_link.get_text(strip=True))
        redir_match = _REDIR_RE.search(href)
        if redir_match:
            external_url = redir_match.group(1)
        else:
            parts = [Part(label="Part 1", url=urljoin(page_url, href))]
    elif no_title_span is not None:
        title = _clean(no_title_span.get_text(strip=True))
        red_status = title_div.find("span", style=re.compile(r"color:\s*red"))
        if red_status is not None:
            status_from_title_block = red_status.get_text(strip=True)

    authors = _split_authors(author_link.get_text(strip=True)) if author_link else []
    author_page_url = urljoin(page_url, author_link["href"]) if author_link else None

    info_div = soup.find("div", id="story_info_line")
    pipe_fields = _parse_pipe_line(info_div.get_text(" ", strip=True)) if info_div else _parse_pipe_line("")

    status = pipe_fields["status"] or status_from_title_block
    notes = None
    if status_from_title_block and pipe_fields["status"] and status_from_title_block != pipe_fields["status"]:
        notes = status_from_title_block

    episodes_div = soup.find("div", id="episodes")
    related_episodes = _clean(_after_label(episodes_div.get_text(" ", strip=True))) if episodes_div else None

    cast_div = soup.find("div", id="cast")
    cast = _clean(_after_label(cast_div.get_text(" ", strip=True))) if cast_div else None

    awards, series_members, ebook_links = None, [], []
    for award_div in soup.find_all("div", id="award_text"):
        label_text = award_div.get_text(" ", strip=True)
        if label_text.startswith("Honors/Awards:"):
            awards = _clean(_after_label(label_text))
        elif label_text.startswith("Series List:"):
            series_members = [Part(label=_clean(a.get_text(strip=True)), url=a["href"])
                               for a in award_div.find_all("a")]
        elif label_text.startswith("EBook Links:"):
            ebook_links = [a["href"] for a in award_div.find_all("a")]
        # "Links:" (cross-posting to other archives) is an explicit non-goal.

    description_div = soup.find("div", id="description")
    summary = _clean(_after_label(description_div.get_text(" ", strip=True))) if description_div else None

    rate_div = soup.find("div", class_="rate_button_line")
    ratings = None
    if rate_div is not None:
        ratings_match = _RATINGS_RE.search(rate_div.get_text(" ", strip=True))
        if ratings_match:
            ratings = {
                "overall": float(ratings_match[1]),
                "overall_count": int(ratings_match[2]),
                "spice": float(ratings_match[3]),
                "spice_count": int(ratings_match[4]),
            }

    return Record(
        source_site=SOURCE_SITE,
        source_id=source_id,
        title=title or "",
        authors=authors,
        author_page_url=author_page_url,
        parts=parts,
        external_url=external_url,
        universe=pipe_fields["universe"],
        era=pipe_fields["era"],
        orientation=pipe_fields["orientation"],
        genre=pipe_fields["genre"],
        length_pages=pipe_fields["length_pages"],
        status=status,
        date=pipe_fields["date"],
        notes=notes,
        related_episodes=related_episodes,
        cast=cast,
        awards=awards,
        series_members=series_members,
        ebook_links=ebook_links,
        ebook_available=bool(ebook_links),
        summary=summary,
        ratings=ratings,
        fetched_from=[page_url],
    )
