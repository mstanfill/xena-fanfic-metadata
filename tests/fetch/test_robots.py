from fanfic_scraper.fetch.robots import parse_robots


def test_allows_everything_when_no_rules_match():
    rules = parse_robots("", "fanfic-metadata-research")
    assert rules.is_allowed("/fiction/titles.html")
    assert rules.crawl_delay is None


def test_disallow_blocks_matching_prefix():
    text = "User-agent: *\nDisallow: /private/\n"
    rules = parse_robots(text, "fanfic-metadata-research")
    assert rules.is_allowed("/fiction/titles.html")
    assert not rules.is_allowed("/private/secret.html")


def test_crawl_delay_parsed_as_float():
    text = "User-agent: *\nCrawl-delay: 10\n"
    rules = parse_robots(text, "fanfic-metadata-research")
    assert rules.crawl_delay == 10.0


def test_specific_agent_block_overrides_wildcard():
    text = (
        "User-agent: *\nDisallow: /everything/\n\n"
        "User-agent: fanfic-metadata-research\nDisallow: /only-us/\n"
    )
    rules = parse_robots(text, "fanfic-metadata-research")
    assert rules.is_allowed("/everything/")
    assert not rules.is_allowed("/only-us/")


def test_grouped_user_agent_lines_share_directives():
    text = "User-agent: a\nUser-agent: b\nDisallow: /blocked/\n"
    rules = parse_robots(text, "b")
    assert not rules.is_allowed("/blocked/")


def test_comments_and_blank_lines_ignored():
    text = "# comment\nUser-agent: *\n\nDisallow: /x/ # trailing comment\n"
    rules = parse_robots(text, "*")
    assert not rules.is_allowed("/x/")
