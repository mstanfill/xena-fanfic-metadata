"""Parser for the xenafan.com titles.html index page.

Markup structure (verified against the live page in October 2026; see
scripts/verify_xenafan.py):

    <div class="entry" data-s="an abnormal fear of eights ukki">
      <div class="story">
        <a class="t" href="content2/eightfear.html">An Abnormal Fear of Eights</a>
        <span class="by">by Ukki</span>
      </div>
    </div>

Each top-level record boundary is a ``div.entry``; there is no need to walk
the A-Z letter-heading anchors (``#LA`` ... ``#LZ``) -- they are a
navigation aid, not how records are delimited.

Within ``div.story``:
  - the title is either ``a.t`` (linked) or ``span.t`` (unlinked, implies a
    ``div.parts`` row holds the real links);
  - an optional ``span.note`` holds a work-type tag (poem/screenplay/song/
    songs/lyric/lyrics), a free-text note ("sequel to X"), or a chapter/part
    range ("Chapter 1-2", "(Part I & II)", "[prologue]");
  - an optional ``span.deadnote`` marks a removed/lost story (it does NOT
    imply a missing author -- see the "file lost to time" case);
  - ``span.by`` is literally "by Author Name" (co-authors joined with
    "and"/"&", which are split into separate authors);
  - an optional ``div.parts`` holds the real per-part links when the title
    itself isn't linked.

One additional real-world wrinkle ("Shape 3"): a single story is
sometimes split across TWO ``div.entry`` blocks that share the same
``data-s`` key, each with a linked title and a chapter-range-shaped
``span.note`` (e.g. "A Bonding Of Hearts" / "Chapter 1-2" and "Chapter
3-6"). These are merged into one
``Record`` with one ``Part`` per entry. The merge only fires when EVERY
entry sharing that ``data-s`` matches the exact shape (linked, no
``div.parts``, chapter-range note, not a deadnote) -- if any entry in the
group doesn't match (e.g. one has no note at all), none of them are merged;
each stays its own record (the live index has 8 such pairs whose second
half is marked "(cont'd)").
"""
from __future__ import annotations

import re

import ftfy
from bs4 import BeautifulSoup

from .schema import Part, Record

SOURCE_SITE = "xenafan"
SOURCE_URL = "https://xenafan.com/fiction/titles.html"

_WORK_TYPES = {"poem", "screenplay", "song", "songs", "lyric", "lyrics"}
_WORK_TYPE_CANON = {"songs": "song", "lyrics": "lyric"}

_CHAPTER_RANGE_RE = re.compile(
    r"^[\(\[]?\s*(chapter|ch\.?|part|scene|act|book|prologue)\b", re.IGNORECASE
)

_BY_PREFIX_RE = re.compile(r"^by\s+", re.IGNORECASE)
_AUTHOR_SPLIT_RE = re.compile(r"\s*&\s*|\s+and\s+", re.IGNORECASE)
_WITH_SUFFIX_RE = re.compile(r"-\s*with\s+(.+)$", re.IGNORECASE)


def _decode(html_bytes: bytes) -> str:
    """Decode raw bytes, preferring a declared <meta charset>, then UTF-8,
    then cp1252/latin-1 as last-resort fallbacks. The live page is genuinely
    UTF-8 despite the HTTP layer reporting ISO-8859-1, so UTF-8 is tried early.
    """
    head = html_bytes[:4096].decode("ascii", errors="ignore")
    match = re.search(r'charset\s*=\s*["\']?\s*([\w-]+)', head, re.IGNORECASE)
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


def _strip_bracketing(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        s = s[1:-1]
    elif len(s) >= 2 and s[0] == "[" and s[-1] == "]":
        s = s[1:-1]
    return s.strip()


def _is_chapter_range(raw_note: str) -> bool:
    return bool(_CHAPTER_RANGE_RE.match(raw_note.strip()))


def _classify_note(raw_note: str):
    """Classify a span.note's raw text into (work_type, free_text_note).

    Exactly one of the two return values is non-None (or both None if the
    note is empty, which shouldn't happen in practice).
    """
    stripped = _strip_bracketing(raw_note)
    lowered = stripped.lower()
    if lowered in _WORK_TYPES:
        return _WORK_TYPE_CANON.get(lowered, lowered), None
    return None, stripped


def _split_authors(by_text: str) -> list[str]:
    text = _BY_PREFIX_RE.sub("", by_text).strip()
    extra = []
    with_match = _WITH_SUFFIX_RE.search(text)
    if with_match:
        extra = [with_match.group(1).strip()]
        text = text[: with_match.start()].strip().rstrip("-").strip()
    authors = [a.strip() for a in _AUTHOR_SPLIT_RE.split(text) if a.strip()]
    authors.extend(extra)
    return authors


def _extract_entry(entry_div) -> dict | None:
    story = entry_div.select_one("div.story")
    if story is None:
        return None

    title_el = story.select_one("a.t") or story.select_one("span.t")
    title = _clean(title_el.get_text()) if title_el else ""
    href = title_el.get("href") if title_el is not None and title_el.name == "a" else None

    note_el = story.select_one("span.note")
    note_raw = _clean(note_el.get_text()) if note_el is not None else None

    deadnote_el = story.select_one("span.deadnote")
    deadnote_raw = _clean(deadnote_el.get_text()) if deadnote_el is not None else None
    if deadnote_raw is not None:
        deadnote_raw = _strip_bracketing(deadnote_raw)

    by_el = story.select_one("span.by")
    authors = _split_authors(_clean(by_el.get_text())) if by_el is not None else []

    parts_div = story.select_one("div.parts")
    parts = []
    if parts_div is not None:
        for a in parts_div.find_all("a"):
            parts.append(Part(label=_clean(a.get_text()), url=a.get("href")))

    return {
        "data_s": entry_div.get("data-s"),
        "title": title,
        "href": href,
        "note_raw": note_raw,
        "deadnote_raw": deadnote_raw,
        "authors": authors,
        "parts": parts,
    }


def _is_mergeable_shape(fields: dict) -> bool:
    """A single entry qualifies for the Shape-3 merge iff it has a linked
    title, no div.parts of its own, a chapter-range-shaped note, and is not
    a deadnote entry."""
    return bool(
        fields["href"]
        and not fields["parts"]
        and fields["note_raw"]
        and _is_chapter_range(fields["note_raw"])
        and not fields["deadnote_raw"]
    )


def _build_record(fields: dict, *, parts_override=None, note_consumed_by_merge=False) -> Record:
    title = fields["title"]
    authors = fields["authors"]
    parts = fields["parts"] if parts_override is None else parts_override

    status = "removed" if fields["deadnote_raw"] else None
    notes = None
    work_type = None

    external_url = None
    href = fields["href"]
    if href and "storylinks.html" in href:
        external_url = href

    # When this entry's span.note has already been consumed as a Part
    # label by the Shape-3 merge, it must NOT also be classified into
    # work_type/notes here.
    if not note_consumed_by_merge and fields["note_raw"] is not None:
        wt, free_text = _classify_note(fields["note_raw"])
        work_type = wt
        notes = free_text

    if fields["deadnote_raw"]:
        notes = fields["deadnote_raw"]

    if href:
        source_id = href
    elif parts:
        source_id = parts[0].url or f"{SOURCE_SITE}:{title}:{authors[0] if authors else ''}"
    elif fields["data_s"]:
        source_id = f"{SOURCE_SITE}:{fields['data_s']}"
    else:
        source_id = f"{SOURCE_SITE}:{title}:{authors[0] if authors else ''}"

    return Record(
        source_site=SOURCE_SITE,
        source_id=source_id,
        title=title,
        title_normalized=title.lower(),
        authors=authors,
        parts=parts,
        work_type=work_type,
        status=status,
        notes=notes,
        external_url=external_url,
        fetched_from=[SOURCE_URL],
    )


def parse_xenafan_titles(html_bytes: bytes) -> list[Record]:
    html_text = _decode(html_bytes)
    soup = BeautifulSoup(html_text, "lxml")

    raw_entries = []
    for entry_div in soup.select("div.entry"):
        fields = _extract_entry(entry_div)
        if fields is not None:
            raw_entries.append(fields)

    # Group entries by data-s to detect the Shape-3 split-chapter merge.
    groups: dict[str, list[int]] = {}
    for idx, fields in enumerate(raw_entries):
        key = fields["data_s"]
        if key:
            groups.setdefault(key, []).append(idx)

    merge_group_for_index: dict[int, list[int]] = {}
    for key, indices in groups.items():
        if len(indices) < 2:
            continue
        if all(_is_mergeable_shape(raw_entries[i]) for i in indices):
            for i in indices:
                merge_group_for_index[i] = indices

    records = []
    handled = set()
    for idx, fields in enumerate(raw_entries):
        if idx in handled:
            continue

        group = merge_group_for_index.get(idx)
        if group is not None:
            merged_parts = []
            for i in group:
                member = raw_entries[i]
                label = _strip_bracketing(member["note_raw"])
                merged_parts.append(Part(label=label, url=member["href"]))
            records.append(
                _build_record(fields, parts_override=merged_parts, note_consumed_by_merge=True)
            )
            handled.update(group)
            continue

        records.append(_build_record(fields))
        handled.add(idx)

    return records
