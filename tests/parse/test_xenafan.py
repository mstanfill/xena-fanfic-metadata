import pytest

from fanfic_scraper.parse.xenafan import parse_xenafan_titles

# Invented entries that reproduce the markup of the real titles.html
# (<div class="entry" data-s="..."> blocks); no real titles or authors.
TITLES_HTML = """<html><body><main>

<!-- Shape 1: simple linked title, no parts, no note -->
<div class="entry" data-s="a fear of sevens quillfeather">
<div class="story"><a class="t" href="content2/sevens.html">A Fear of Sevens</a><span class="by">by Quillfeather</span></div>
</div>

<!-- Shape 1 + work-type tag (poem) -->
<div class="entry" data-s="the journey starts robin (wren)">
<div class="story"><a class="t" href="content/journeystarts.htm">The Journey Starts</a><span class="note">(poem)</span><span class="by">by Robin (Wren)</span></div>
</div>

<!-- Shape 2: unlinked title + parts row + non-work-type note (sequel note) -->
<div class="entry" data-s="ex nihilo lanternbard">
<div class="story"><span class="t">Ex Nihilo</span><span class="note">(sequel to Beginnings)</span><span class="by">by Lanternbard</span><div class="parts"><a href="content5/lantern_exnihilo1.html">Part I</a><a href="content5/lantern_exnihilo2.html">Part II</a><a href="content5/lantern_exnihilo3.html">Part III</a><a href="content5/lantern_exnihilo4.html">Part IV</a><a href="content5/lantern_exnihilo5.html">Part V</a><a href="content5/lantern_exnihilo6.html">Part VI</a><a href="content5/lantern_exnihilo7.html">Part VII</a></div></div>
</div>

<!-- Shape 3: chapter-range split across two entries sharing the same data-s; must merge into one Record -->
<div class="entry" data-s="a meeting of minds tidewriter">
<div class="story"><a class="t" href="content5/tide_minds1.html">A Meeting Of Minds</a><span class="note">Chapter 1-2</span><span class="by">by Tidewriter</span></div>
</div>
<div class="entry" data-s="a meeting of minds tidewriter">
<div class="story"><a class="t" href="content5/tide_minds2.html">A Meeting Of Minds</a><span class="note">Chapter 3-6</span><span class="by">by Tidewriter</span></div>
</div>

<!-- deadnote / file lost to time: has a normal author despite being removed -->
<div class="entry" data-s="a picnic by the river oldscroll">
<div class="story"><span class="t">A Picnic By The River</span><span class="by">by OldScroll</span> <span class="deadnote">(file lost to time)</span></div>
</div>

<!-- External story: links to list/storylinks.html#anchor -->
<div class="entry" data-s="the messenger's delay bluequill">
<div class="story"><a class="t" href="list/storylinks.html#bluequill">The Messenger's Delay</a><span class="by">by Bluequill</span></div>
</div>

<!-- Same story listed under two spellings of the author: must NOT be deduped at parse time -->
<div class="entry" data-s="songs of frost and flame starryhope">
<div class="story"><a class="t" href="content5/starryhope_frost.html">Songs of Frost and Flame</a><span class="by">by StarryHOPE</span></div>
</div>
<div class="entry" data-s="songs of frost and flame staryhope">
<div class="story"><a class="t" href="content5/starryhope_frost.html">Songs of Frost and Flame</a><span class="by">by StaryHOPE</span></div>
</div>

<!-- Listed twice with different titles and data-s: must NOT be deduped -->
<div class="entry" data-s="warm hands...cold night ember max">
<div class="story"><span class="t">Warm Hands...Cold Night</span><span class="by">by Ember Max</span><div class="parts"><a href="content5/ember_hands1.html">Scene 1-18</a></div></div>
</div>
<div class="entry" data-s="warm hands...cold night - scene 1-18 ember max">
<div class="story"><a class="t" href="content5/ember_hands1.html">Warm Hands...Cold Night - Scene 1-18</a><span class="by">by Ember Max</span></div>
</div>

<!-- data-s collision that must NOT trigger the Shape 3 merge: the first entry has no note
     and the second has "(cont'd)", so neither matches the chapter-range pattern. -->
<div class="entry" data-s="voyage of a season harborbard">
<div class="story"><a class="t" href="content5/harbor_voyage1.html">Voyage of a Season</a><span class="by">by Harborbard</span></div>
</div>
<div class="entry" data-s="voyage of a season harborbard">
<div class="story"><a class="t" href="content5/harbor_voyage2.html">Voyage of a Season</a><span class="note">(cont'd)</span><span class="by">by Harborbard</span></div>
</div>

<!-- Standalone chapter-range-shaped note with no sibling sharing its data-s: goes to notes as free text -->
<div class="entry" data-s="a wandering amazon jo example (goldfinch)">
<div class="story"><a class="t" href="content/wanderamazon.htm">A Wandering Amazon</a><span class="note">(Part I &amp; II)</span><span class="by">by Jo Example (Goldfinch)</span></div>
</div>

<!-- Co-authored story ("by Fern and RT"): authors list is split on "and" -->
<div class="entry" data-s="longing fern and rt">
<div class="story"><a class="t" href="content5/fernrt_longing.html">Longing</a><span class="by">by Fern and RT</span></div>
</div>

</main></body></html>
""".encode("utf-8")


@pytest.fixture(scope="module")
def records():
    return parse_xenafan_titles(TITLES_HTML)


def by_href_fragment(records, fragment):
    """Find the single record whose parts or source_id reference a URL
    containing `fragment`. Raises if not exactly one match."""
    matches = []
    for r in records:
        urls = [p.url for p in r.parts if p.url] + ([r.source_id] if r.source_id else [])
        if any(fragment in u for u in urls if u):
            matches.append(r)
    assert len(matches) == 1, f"expected exactly 1 record matching {fragment!r}, got {len(matches)}"
    return matches[0]


def test_total_record_count_no_entries_silently_dropped(records):
    # 15 raw <div class="entry"> blocks; the two "A Meeting Of Minds"
    # entries merge into one record (Shape 3), so every entry is accounted
    # for in 14 records.
    assert len(records) == 14


def test_shape1_simple_linked_title_no_parts(records):
    r = by_href_fragment(records, "sevens.html")
    assert r.title == "A Fear of Sevens"
    assert r.authors == ["Quillfeather"]
    assert r.parts == []
    assert r.work_type is None
    assert r.source_site == "xenafan"
    assert r.status is None
    assert r.external_url is None


def test_shape1_with_work_type_tag_poem(records):
    r = by_href_fragment(records, "journeystarts.htm")
    assert r.title == "The Journey Starts"
    assert r.authors == ["Robin (Wren)"]
    assert r.work_type == "poem"
    assert r.parts == []


def test_shape2_unlinked_title_with_parts_and_non_worktype_note(records):
    r = by_href_fragment(records, "lantern_exnihilo1.html")
    assert r.title == "Ex Nihilo"
    assert r.authors == ["Lanternbard"]
    assert r.work_type is None
    assert r.notes == "sequel to Beginnings"
    assert [p.label for p in r.parts] == [
        "Part I", "Part II", "Part III", "Part IV", "Part V", "Part VI", "Part VII",
    ]
    assert r.parts[0].url == "content5/lantern_exnihilo1.html"
    assert r.parts[6].url == "content5/lantern_exnihilo7.html"


def test_shape3_merge_chapter_range_entries_into_one_record(records):
    r = by_href_fragment(records, "tide_minds1.html")
    assert r.title == "A Meeting Of Minds"
    assert r.authors == ["Tidewriter"]
    assert len(r.parts) == 2
    assert r.parts[0].label == "Chapter 1-2"
    assert r.parts[0].url == "content5/tide_minds1.html"
    assert r.parts[1].label == "Chapter 3-6"
    assert r.parts[1].url == "content5/tide_minds2.html"

    # confirm the merge really produced ONE record, not two
    titles = [x.title for x in records if x.title == "A Meeting Of Minds"]
    assert len(titles) == 1


def test_deadnote_file_lost_to_time_has_normal_author(records):
    matches = [r for r in records if r.title == "A Picnic By The River"]
    assert len(matches) == 1
    r = matches[0]
    assert r.authors == ["OldScroll"]  # deadnote entries DO have an author
    assert r.status == "removed"
    assert r.notes == "file lost to time"
    assert r.parts == []


def test_external_storylinks_entry(records):
    matches = [r for r in records if r.title == "The Messenger's Delay"]
    assert len(matches) == 1
    r = matches[0]
    assert r.authors == ["Bluequill"]
    assert r.external_url == "list/storylinks.html#bluequill"
    assert r.parts == []


def test_author_spelling_variant_duplicate_not_deduped(records):
    matches = [r for r in records if r.title == "Songs of Frost and Flame"]
    assert len(matches) == 2
    authors = sorted(r.authors[0] for r in matches)
    assert authors == ["StarryHOPE", "StaryHOPE"]


def test_retitled_duplicate_not_deduped(records):
    matches = [r for r in records if "Warm Hands" in r.title]
    assert len(matches) == 2
    titles = sorted(r.title for r in matches)
    assert titles == ["Warm Hands...Cold Night", "Warm Hands...Cold Night - Scene 1-18"]


def test_data_s_collision_without_matching_shape_is_not_merged(records):
    # Two entries share data-s "voyage of a season harborbard" but the
    # first has no note at all (not a chapter-range shape), so they must
    # NOT be merged by the Shape 3 logic -- stay as two separate records.
    matches = [r for r in records if r.title == "Voyage of a Season"]
    assert len(matches) == 2
    source_ids_or_hrefs = sorted(r.source_id for r in matches)
    assert any("harbor_voyage1.html" in s for s in source_ids_or_hrefs)
    assert any("harbor_voyage2.html" in s for s in source_ids_or_hrefs)
    for r in matches:
        assert r.parts == []


def test_standalone_chapter_range_note_without_merge_partner_goes_to_notes(records):
    r = by_href_fragment(records, "wanderamazon.htm")
    assert r.title == "A Wandering Amazon"
    assert r.authors == ["Jo Example (Goldfinch)"]
    assert r.notes == "Part I & II"
    assert r.parts == []
    assert r.work_type is None


def test_coauthors_split_on_and(records):
    r = by_href_fragment(records, "fernrt_longing.html")
    assert r.title == "Longing"
    assert r.authors == ["Fern", "RT"]
