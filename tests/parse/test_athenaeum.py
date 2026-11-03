from fanfic_scraper.parse.athenaeum import parse_athenaeum_search_page

# Invented records that reproduce the markup of a real search-results page;
# no real titles or authors.
FIXTURE = """<html><body>
<div id="pagination">search results header / pagination widget, ignored (before the first record)</div>

<A href="comments.cfm?I_KEY=6823&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=6823&command=add_story" class="comments">Bookshelf</a>&nbsp;&nbsp;<a href="watched_stories.cfm?command=add_story_to_watched_list&story_index=6823" target="_blank">Watch</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/rj_example_the_mira_puzzle.html"></a>
<A href="http://xenafiction.net/scrolls/rj_example_the_mira_puzzle.html" target="_blank" class="title">&#39;Mira&#39; Puzzle (The)</A>&nbsp;
by <a href="author_pages/rjexample.html" class="author" id="author">R. J. Example</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Original / Uber | Futuristic | Alternative | Drama | Novella - 93 pages | Finished | Mar-10
</SPAN></DIV>
<DIV id="award_text"><SPAN class="award_text">Honors/Awards:</SPAN> <SPAN class="story_line">     #47 in 2010 &nbsp;<br></SPAN></DIV>
<div class="rate_button_line"><span class="story_line">Fan Ratings: &nbsp;&nbsp;&nbsp; Overall: <span class="award_text">9.13</span> (Rated 22 times) &nbsp;&nbsp;&nbsp;Spice Index: <span class="award_text">5.92</span> (Rated 14 times)</span> </div>
&nbsp;&nbsp;&nbsp;<span class="story_line"><a href="comments.cfm?I_KEY=6823&command=enter">Rate</a></span>
<DIV id="award_text"><SPAN class="story_line">EBook Links:</SPAN>
<a href="http://xenafiction.net/scrolls/rj_example_the_mira_puzzle.epub">.epub</a>&nbsp;&nbsp;
<a href="http://xenafiction.net/scrolls/rj_example_the_mira_puzzle.pdf">.pdf</a>&nbsp;&nbsp;
</DIV>
<DIV id="description" class="teaser_block"><SPAN class="story_line">Teaser: &nbsp;</SPAN><SPAN class="story_line">An invented teaser about a puzzle and a stranger.</SPAN></DIV>

<A href="comments.cfm?I_KEY=7382&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=7382&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://www.example.com/MindReaching.HTM"></a>
<A href="http://xenafiction.net/redir.cfm?sn=7382&ex_site=http://www.example.com/MindReaching.HTM" target="_blank" class="title">(A Mind Reaching Out) </A>&nbsp;
by <a href="author_pages/farquill.html" class="author" id="author">Farquill</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Modern | Alternative | Romance | Short Story - 20 pages | Finished | Jan-05
</SPAN></DIV>

<A href="comments.cfm?I_KEY=3834&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=3834&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://www.xenafiction.net/scrolls/published_example.html"></a>
<span class="no_title">Redemption Example</span>&nbsp;
by <a href="author_pages/publishedauthor.html" class="author" id="author">Published Author</A><br><span style="color: red;">Published</span>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Original / Uber | Modern | Alternative | Romance (alt) | Novel - 162 pages | Finished | Mar-01
</SPAN></DIV>

<A href="comments.cfm?I_KEY=4242&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=4242&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://www.xenafiction.net/scrolls/bare_example.html"></a>
<span class="no_title">A Bare Example</span>&nbsp;
by <a href="author_pages/bareauthor.html" class="author" id="author">Bare Author</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena
</SPAN></DIV>

<A href="comments.cfm?I_KEY=8888&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=8888&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/no_era_example.html"></a>
<A href="http://xenafiction.net/scrolls/no_era_example.html" target="_blank" class="title">No Era Example</A>&nbsp;
by <a href="author_pages/noeraauthor.html" class="author" id="author">No Era Author</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Alternative | Adventure | Novel - 240 pages | Finished | Feb-98
</SPAN></DIV>

<A href="comments.cfm?I_KEY=5555&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=5555&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/episodes_cast_example.html"></a>
<A href="http://xenafiction.net/scrolls/episodes_cast_example.html" target="_blank" class="title">Episodes And Cast Example</A>&nbsp;
by <a href="author_pages/episodesauthor.html" class="author" id="author">Episodes Author</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Finished
</SPAN></DIV>
<DIV id="episodes"><SPAN class="story_line">Related Episodes:</SPAN> <SPAN class="story_line">Sins of the Past</SPAN></div><DIV id="cast"><SPAN class="story_line">Cast:</SPAN> <SPAN class="story_line">Xena, Gabrielle</SPAN></DIV>

<A href="comments.cfm?I_KEY=7777&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=7777&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/series_example.html"></a>
<A href="http://xenafiction.net/scrolls/series_example.html" target="_blank" class="title">Series Example</A>&nbsp;
by <a href="author_pages/samexample.html" class="author" id="author">Sam Example</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Original / Uber | Finished
</SPAN></DIV>
<DIV id="award_text"><SPAN class="story_line">Series List:</SPAN> <SPAN class="story_line"><a href="http://xenafiction.net/scrolls/sam_example_sfr1.html">Song for Remembering (A)</a>, <a href="http://xenafiction.net/scrolls/sam_example_arfhe.html">...and A Roof For Happy Endings</a></SPAN></DIV>

<A href="comments.cfm?I_KEY=9001&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=9001&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/below_threshold_example.html"></a>
<A href="http://xenafiction.net/scrolls/below_threshold_example.html" target="_blank" class="title">Below Threshold Example</A>&nbsp;
by <a href="author_pages/newauthor.html" class="author" id="author">New Author</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Finished
</SPAN></DIV>
<div class="rate_button_line"><span class="story_line">Fan Rating: N/A (Rated 1 time.  Needs 4 more to show Fan Rating)</span></div>

<A href="comments.cfm?I_KEY=1212&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=1212&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/coauthor_example.html"></a>
<A href="http://xenafiction.net/scrolls/coauthor_example.html" target="_blank" class="title">Co-Author Example</A>&nbsp;
by <a href="author_pages/rooklantern.html" class="author" id="author">Rook Lantern and WordSmith</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Finished
</SPAN></DIV>

<A href="comments.cfm?I_KEY=6666&command=enter" class="comments">Recommend</A>&nbsp;&nbsp;<a href="favorites.cfm?I_KEY=6666&command=add_story" class="comments">Bookshelf</a>
</DIV>
<div id="title" style="vertical-align: top;">
<a name="http://xenafiction.net/scrolls/mojibake_example.html"></a>
<A href="http://xenafiction.net/scrolls/mojibake_example.html" target="_blank" class="title">Mojibake Example</A>&nbsp;
by <a href="author_pages/mojibakeauthor.html" class="author" id="author">Mojibake Author</A>
</DIV>
<DIV id="story_info_line"><SPAN class="story_line">
	 Xena | Finished
</SPAN></DIV>
<DIV id="description" class="teaser_block"><SPAN class="story_line">Teaser: &nbsp;</SPAN><SPAN class="story_line">She doesnâ€™t know it yet, but everything is about to change.</SPAN></DIV>

</body></html>
""".encode("utf-8")
PAGE_URL = "http://xenafiction.net/styles/athenaeum_deepblue/athenaeum_search_v1.cfm"


def _record(source_id):
    return next(r for r in parse_athenaeum_search_page(FIXTURE, PAGE_URL) if r.source_id == source_id)


def test_hosted_story_has_a_part_and_decodes_html_entities_in_the_title():
    r = _record("6823")
    assert r.source_site == "athenaeum"
    assert r.title == "'Mira' Puzzle (The)"
    assert r.external_url is None
    assert r.parts[0].url.endswith(".html")
    assert r.author_page_url.startswith(
        "http://xenafiction.net/styles/athenaeum_deepblue/author_pages/"
    )
    assert r.universe == "Original / Uber"
    assert r.era == "Futuristic"
    assert r.orientation == "Alternative"
    assert r.genre == "Drama"
    assert r.length_pages == 93
    assert r.status == "Finished"
    assert r.date == "Mar-10"


def test_offsite_story_sets_external_url_and_no_parts():
    r = _record("7382")
    assert r.external_url == "http://www.example.com/MindReaching.HTM"
    assert r.parts == []


def test_no_link_published_story_prefers_pipe_status_and_notes_the_disagreement():
    r = _record("3834")
    assert r.parts == []
    assert r.external_url is None
    assert r.status == "Finished"
    assert r.notes and "Published" in r.notes


def test_bare_no_link_no_status_record_does_not_crash():
    r = _record("4242")
    assert r.title
    assert r.authors


def test_pipe_line_missing_era_does_not_shift_other_fields():
    r = _record("8888")
    assert r.universe == "Xena"
    assert r.era is None
    assert r.orientation == "Alternative"
    assert r.genre == "Adventure"
    assert r.length_pages == 240
    assert r.status == "Finished"
    assert r.date == "Feb-98"


def test_optional_labeled_fields_and_dual_ratings():
    r = _record("6823")
    assert r.awards
    assert r.ebook_available is True
    assert r.ebook_links[0].endswith(".epub")
    assert r.ratings == {"overall": 9.13, "overall_count": 22, "spice": 5.92, "spice_count": 14}
    assert r.summary


def test_episodes_and_cast():
    r = _record("5555")
    assert r.related_episodes
    assert r.cast


def test_series_members_captured_as_parts():
    r = _record("7777")
    assert len(r.series_members) == 2
    assert r.series_members[0].label
    assert r.series_members[0].url.startswith("http")


def test_below_threshold_rating_is_none_not_partial():
    r = _record("9001")
    assert r.ratings is None


def test_coauthors_joined_by_and_are_split():
    r = _record("1212")
    assert r.authors == ["Rook Lantern", "WordSmith"]


def test_mojibake_in_text_fields_is_repaired():
    r = _record("6666")
    assert "â€™" not in r.summary
    assert "doesn't know it yet" in r.summary
