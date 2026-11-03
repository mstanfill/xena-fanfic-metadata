"""Parser for a xenafan.com story page (part 1 only), used to enrich the
titles.html records with the header block at the top of each story.

The structure below comes from a manual look at story pages such as
``content5/cruise_abinitio1.html``. Markup varies across the site's many
eras, so the selectors are kept deliberately generic:

  - ``<meta name="author">`` is reliable; ``<meta name="description">`` is
    generic ("short story") and ignored;
  - a free-text header (disclaimer, sequel notes, age warnings, song
    credits, author email) sits above the first ``<hr>``;
  - a part-navigation row links every part, sometimes one more than the
    index lists;
  - a footer links to the author's listing (``list/bardlistc.html#cruise``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import PreformattedString

from .schema import Part
from .xenafan import _clean, _decode

_STORY_FILE_RE = re.compile(r"\.html?$", re.IGNORECASE)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


@dataclass
class StoryHeader:
    url: str
    page_title: str | None = None
    meta_author: str | None = None
    disclaimer_text: str | None = None
    author_emails: list = field(default_factory=list)
    nav_parts: list = field(default_factory=list)  # list[Part]
    author_listing_url: str | None = None
    warnings: list = field(default_factory=list)


_BLOCK_TAGS = {
    "p", "div", "center", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "tr", "table", "blockquote", "pre", "ul", "ol", "dl", "dt", "dd",
}


def _node_text(node) -> str:
    """Visible text with line breaks only at block elements and <br>, so
    inline tags (<a>, <b>, <font>) don't split a sentence across lines."""
    if isinstance(node, PreformattedString):  # comments, doctype, CDATA
        return ""
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node))  # source newlines render as spaces
    if not isinstance(node, Tag) or node.name in ("script", "style"):
        return ""
    inner = "".join(_node_text(child) for child in node.children)
    return f"\n{inner}\n" if node.name in _BLOCK_TAGS else inner


def _text_lines(nodes) -> str:
    """Join the visible text of `nodes`, one cleaned line per block/<br>."""
    text = "".join(_node_text(node) for node in nodes)
    lines = [_clean(line) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _header_nodes(body: Tag, first_hr: Tag) -> list:
    """Everything in document order before `first_hr`, as the top-most
    nodes (so text isn't counted twice through nested ancestors)."""
    nodes = []
    current = first_hr
    while current is not None and current is not body:
        nodes[:0] = list(current.previous_siblings)[::-1]
        current = current.parent
    return nodes


def _same_dir_story_link(href: str, page_url: str) -> str | None:
    absolute = urljoin(page_url, href)
    page, link = urlsplit(page_url), urlsplit(absolute)
    if link.netloc != page.netloc or not _STORY_FILE_RE.search(link.path):
        return None
    if link.path.rsplit("/", 1)[0].lower() != page.path.rsplit("/", 1)[0].lower():
        return None
    return absolute.split("#", 1)[0]


def parse_xenafan_story(html_bytes: bytes, url: str) -> StoryHeader:
    soup = BeautifulSoup(_decode(html_bytes), "lxml")
    header = StoryHeader(url=url)

    if soup.title and soup.title.string:
        header.page_title = _clean(soup.title.string) or None

    author_meta = soup.find("meta", attrs={"name": re.compile(r"^author$", re.I)})
    if author_meta and author_meta.get("content"):
        header.meta_author = _clean(author_meta["content"]) or None

    body = soup.body or soup
    first_hr = body.find("hr")
    header_links = set()
    if first_hr is None:
        header.warnings.append("no <hr> found; header block not extracted")
    else:
        nodes = _header_nodes(body, first_hr)
        for node in nodes:
            if isinstance(node, Tag):
                header_links.update(id(a) for a in node.find_all("a"))
                if node.name == "a":
                    header_links.add(id(node))
        text = _text_lines(nodes)
        header.disclaimer_text = text or None
        if text:
            header.author_emails = sorted(set(_EMAIL_RE.findall(text)))

    seen = set()
    for a in body.find_all("a", href=True):
        href = a["href"]
        if "bardlist" in href.lower() and header.author_listing_url is None:
            header.author_listing_url = urljoin(url, href)
            continue
        # Links in the header ("sequel to X") aren't part navigation.
        if id(a) in header_links:
            continue
        target = _same_dir_story_link(href, url)
        if target is None or target.lower() in seen:
            continue
        seen.add(target.lower())
        header.nav_parts.append(Part(label=_clean(a.get_text()), url=target))

    return header


def apply_story_header(record, header: StoryHeader, cache_key: str) -> None:
    """Copy the story-page header onto a titles.html Record in place,
    noting any disagreement with the index rather than overwriting it."""
    record.disclaimer_text = header.disclaimer_text
    if header.author_listing_url:
        record.author_page_url = header.author_listing_url
    if cache_key not in record.fetched_from:
        record.fetched_from.append(cache_key)

    notes = [record.notes] if record.notes else []
    if header.meta_author and header.meta_author.lower() not in (a.lower() for a in record.authors):
        notes.append(f"story page meta author: {header.meta_author}")
    if len(header.nav_parts) > 1 and len(header.nav_parts) != len(record.parts):
        labels = ", ".join(p.label for p in header.nav_parts)
        notes.append(
            f"story page nav lists {len(header.nav_parts)} parts, index lists "
            f"{len(record.parts)}: {labels}"
        )
    notes.extend(header.warnings)
    record.notes = "; ".join(notes) or None
