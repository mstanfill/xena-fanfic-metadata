from fanfic_scraper.parse.academy import last_updated_date, parse_author_page

# Invented author pages that reproduce the markup of real Academy pages
# (including the two different generators); no real titles or authors.
TIDEWRITER = """<!DOCTYPE html PUBLIC "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
  <meta http-equiv="Content-Type"
 content="text/html; charset=iso-8859-1">
  <meta name="description" content="Academy Author Page">
  <meta name="GENERATOR"
 content="Mozilla/4.76 [en] (Win98; U) [Netscape]">
  <title>Tidewriter</title>
</head>
<body>
<p id="index">Academy Author Index</p>
<p id="author"><a href="mailto:tidewriter@example.com">Tidewriter</a></p>
<p id="update">Last Updated:&nbsp; 1/28/2008<br>
</p>
<hr>
<p id="title"><a href="../fanfic/t/tide_longseason1.html">Long Season</a>
&nbsp;&nbsp;<span id="incomplete">[Incomplete]</span></p>
<p id="contence">An invented summary for a story split into many parts,
with its part links wrapped across several rows.</p>
<p id="parts">
<a href="../fanfic/t/tide_longseason1.html">Part 1</a>&nbsp;
<a href="../fanfic/t/tide_longseason2.html">Part 2</a>&nbsp;
<a href="../fanfic/t/tide_longseason3.html">Part 3</a>&nbsp;
<a href="../fanfic/t/tide_longseason4.html">Part 4</a>&nbsp;
<a href="../fanfic/t/tide_longseason5.html">Part 5</a>&nbsp;
<a href="../fanfic/t/tide_longseason6.html">Part 6</a>&nbsp;
<a href="../fanfic/t/tide_longseason7.html">Part 7</a>&nbsp;
<a href="../fanfic/t/tide_longseason8.html">Part 8</a>&nbsp;
<a href="../fanfic/t/tide_longseason9.html">Part 9</a>&nbsp;
<a href="../fanfic/t/tide_longseason10.html">Part 10</a>&nbsp;
<a href="../fanfic/t/tide_longseason11.html">Part 11</a>&nbsp;
<a href="../fanfic/t/tide_longseason12.html">Part 12</a>&nbsp;
<a href="../fanfic/t/tide_longseason13.html">Part 13</a>&nbsp;</p>
<p id="parts">
<a href="../fanfic/t/tide_longseason14.html">Part 14</a>&nbsp;
<a href="../fanfic/t/tide_longseason15.html">Part 15</a>&nbsp;
<a href="../fanfic/t/tide_longseason16.html">Part 16</a>&nbsp;
<a href="../fanfic/t/tide_longseason17.html">Part 17</a>&nbsp;
<a href="../fanfic/t/tide_longseason18.html">Part 18</a>&nbsp;
<a href="../fanfic/t/tide_longseason19.html">Part 19</a>&nbsp;
<a href="../fanfic/t/tide_longseason20.html">Part 20</a>&nbsp;
<a href="../fanfic/t/tide_longseason21.html">Part 21</a>&nbsp;
<a href="../fanfic/t/tide_longseason22.html">Part 22</a>&nbsp;
<a href="../fanfic/t/tide_longseason23.html">Part 23</a>&nbsp;
<a href="../fanfic/t/tide_longseason24.html">Part 24</a>&nbsp;
<a href="../fanfic/t/tide_longseason25.html">Part 25</a>&nbsp;
<a href="../fanfic/t/tide_longseason26.html">Part 26</a>&nbsp;
</p>
<p id="parts">
<a href="../fanfic/t/tide_longseason27.html">Part 27</a>&nbsp;
<a href="../fanfic/t/tide_longseason28.html">Part 28</a>&nbsp;
<a href="../fanfic/t/tide_longseason29.html">Part 29</a>&nbsp;
<a href="../fanfic/t/tide_longseason30.html">Part 30</a>&nbsp;
<a href="../fanfic/t/tide_longseason31.html">Part 31</a>&nbsp;
<a href="../fanfic/t/tide_longseason32.html">Part 32</a>&nbsp;
<a href="../fanfic/t/tide_longseason33.html">Part 33</a>&nbsp;
<a href="../fanfic/t/tide_longseason34.html">Part 34</a>&nbsp;
<a href="../fanfic/t/tide_longseason35.html">Part 35</a>&nbsp;
<a href="../fanfic/t/tide_longseason36.html">Part 36</a>&nbsp;
<a href="../fanfic/t/tide_longseason37.html">Part 37</a>&nbsp;
<a href="../fanfic/t/tide_longseason38.html">Part 38</a>&nbsp;
</p>
<p id="title"><a href="../contest/2003/bardcon/tide_nighttrain3.html">Night
Train</a> &nbsp;&nbsp;<span id="note">[Academy 101 Story Premise]</span></p>
<p id="contence">An invented contest entry.</p>
<p id="title"><a href="../fanfic/t/tide_mirrorfaces.html">Mirror
Faces</a> &nbsp;&nbsp;<span id="incomplete">[Incomplete]</span></p>
<p id="contence">An invented unfinished story.</p>
<p id="parts">
<a href="../fanfic/t/tide_mirrorfaces.html">Part 0</a>&nbsp;
<a href="../fanfic/t/tide_mirrorfaces1.html">Part 1</a>&nbsp;
<a href="../fanfic/t/tide_mirrorfaces2.html">Part 2</a>&nbsp;
<a href="../fanfic/t/tide_mirrorfaces3.html">Part 3</a>&nbsp;</p>
<p id="series">Harbor And Lighthouse Series &nbsp;&nbsp;<a
 href="../ebooks/index.html"><img id="ebook" src="ebook.gif"
 alt="ebook version available"></a></p>
<div id="inset">
<p id="title"><a href="../fanfic/t/tide_firstlight.html">First Light</a></p>
<p id="contence">A prequel to <a
 href="../fanfic/t/tide_undertow1.html">Undertow</a>, invented for tests.</p>
<p id="title"><a href="../fanfic/t/tide_undertow1.html">Undertow</a></p>
<p id="contence">The middle story of an invented series.</p>
<p id="parts">
<a href="../fanfic/t/tide_undertow1.html">Part 1</a>&nbsp;
<a href="../fanfic/t/tide_undertow2.html">Part 2</a>&nbsp;
<a href="../fanfic/t/tide_undertow3.html">Part 3</a>&nbsp;
<a href="../fanfic/t/tide_undertow4.html">Part 4</a>&nbsp;
<a href="../fanfic/t/tide_undertow5.html">Part 5</a>&nbsp;
<a href="../fanfic/t/tide_undertow6.html">Part 6</a>&nbsp;</p>
<p id="title"><a href="../fanfic/t/tide_hightide1.html">High Tide</a></p>
<p id="contence">The <i>sequel</i> to <a
 href="../fanfic/t/tide_undertow1.html">Undertow</a>.</p>
<p id="parts">
<a href="../fanfic/t/tide_hightide1.html">Part 1</a>&nbsp;
<a href="../fanfic/t/tide_hightide2.html">Part 2</a>&nbsp;
<a href="../fanfic/t/tide_hightide3.html">Part 3</a>&nbsp;
<a href="../fanfic/t/tide_hightide4.html">Part 4</a>&nbsp;
<a href="../fanfic/t/tide_hightide5.html">Part 5</a>&nbsp;
<a href="../fanfic/t/tide_hightide6.html">Part 6</a>&nbsp;
<a href="../fanfic/t/tide_hightide7.html">Part 7</a>&nbsp;
<a href="../fanfic/t/tide_hightide8.html">Part 8</a>&nbsp;</p>
</div>
<p id="title"><a href="../fanfic/t/tide_aftertheseries.html">After The
Series</a></p>
<p id="contence">Placed after the series div closes, to confirm that a
story outside the inset div has no series.</p>
</body>
</html>""".encode("latin-1")

LANTERN = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><head><title>Jo Example</title>
<meta http-equiv=Content-Type content="text/html; charset=unicode">
<meta content="Academy Author Page" name=description>
<meta content="MSHTML 6.00.6000.17023" name=GENERATOR></head>
<body>
<p id="index"> <a href="../halloffame"><img id="fame" src="../halloffame/trophy.jpg" align="left"></a> 
<span  style="margin-left: -99px;">Academy Author Index</span></p>
<p id="author"><span style="margin-left: -99px;">
<a href="mailto:lantern@example.com">Lantern</a></span></p>
<p id="update"><span style="margin-left: -99px;">Last Updated:&nbsp;8/31/2014</span></p>
<p id="update"> <span style="margin-left: -99px;"><!--achievement, other-->&nbsp;</span><br>
<span style="margin-left: -99px;">2014 Lifetime Achievement<span><br>
<span style="margin-left: -99px;">2005 Hall of Fame - Author<span><br>
<span style="margin-left: -99px;"> Stories - An Invented Title</span><br>
<span style="margin-left: -99px;"><br>
<p id="fame_web"><span style="margin-left: +25px;"> <a href="http://www.example.com">Author's web site</a></span></p>
<HR>


<p id="title"><a href="../fanfic/r/re_lantern_pim.html">Partners In Mischief</a> <span id="with"> - with R. Example</span>&nbsp;&nbsp; <span
 id="note">[Academy April Fools]</span> &nbsp;&nbsp;<a  href="../ebooks/index.html"><img id="ebook" src="ebook.gif"
 alt="ebook version available"></a></p>
<p id="contence">An invented comedy about two people who set out to undo a lifetime of mischief.</p>
<p id="title"><a href="../fanfic/l/lantern_spell.html">A Friend's Spell</a></p>
<p id="contence">An invented children's tale about friendship.</p>
</body>
</html>""".encode("latin-1")

TIDEWRITER_URL = "http://www.academyofbards.org/authors/tidewriter.html"
LANTERN_URL = "http://www.academyofbards.org/authors/lantern.html"


def _story(html_bytes, page_url, display_names, title_substring):
    return next(r for r in parse_author_page(html_bytes, page_url, display_names) if title_substring in r.title)


def test_author_page_name_is_ignored_in_favor_of_index_aliases():
    # The page's own <p id="author"> mailto link text is "Tidewriter" -- use a
    # display_names value that diverges from that page text, so this test
    # would fail if the implementation ever re-derived authors from the page
    # instead of using the display_names parameter.
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tide Smith"], "Night Train")
    assert r.authors == ["Tide Smith"]


def test_many_part_story_concatenates_consecutive_parts_blocks():
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Long Season")
    assert len(r.parts) == 38
    assert r.parts[0].label == "Part 1"
    assert r.parts[-1].label == "Part 38"


def test_bracket_tag_that_is_not_a_known_work_type_goes_to_notes():
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Night Train")
    assert r.work_type is None
    assert r.notes and "Academy 101 Story Premise" in r.notes


def test_incomplete_tag_sets_status():
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Mirror Faces")
    assert r.status == "incomplete"


def test_last_updated_date_is_the_single_update_block():
    assert last_updated_date(TIDEWRITER) == "1/28/2008"


def test_last_updated_date_skips_the_second_unrelated_update_block():
    # The page's second id="update" block is Hall-of-Fame text with no
    # "Last Updated:" text at all -- it must not be mistaken for the date,
    # and parse_author_page must not crash walking past it either.
    assert last_updated_date(LANTERN) == "8/31/2014"
    records = parse_author_page(LANTERN, LANTERN_URL, ["Lantern"])
    assert len(records) == 2  # "Partners In Mischief", "A Friend's Spell"


def test_coauthor_suffix_and_ebook_icon_and_note_together():
    r = _story(LANTERN, LANTERN_URL, ["Lantern"], "Partners In Mischief")
    assert "R. Example" in (r.notes or "")
    assert r.ebook_available is True
    assert "Academy April Fools" in (r.notes or "")


def test_bare_story_with_no_optional_markup():
    r = _story(LANTERN, LANTERN_URL, ["Lantern"], "A Friend's Spell")
    assert r.summary
    assert r.ebook_available is False
    assert r.notes is None


def test_series_members_are_tagged_with_the_series_name():
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Undertow")
    assert r.series == "Harbor And Lighthouse Series"


def test_series_members_list_the_other_members_not_itself():
    r = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Undertow")
    titles = {m.label for m in r.series_members}
    assert titles == {"First Light", "High Tide"}


def test_story_before_and_after_the_series_div_has_no_series():
    before = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "Long Season")
    after = _story(TIDEWRITER, TIDEWRITER_URL, ["Tidewriter"], "After The Series")
    assert before.series is None
    assert after.series is None
