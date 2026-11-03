from fanfic_scraper.fetch.config import ACADEMY, ATHENAEUM, XENAFAN, SiteConfig, user_agent_for


def test_xenafan_config_values():
    assert isinstance(XENAFAN, SiteConfig)
    assert XENAFAN.host == "xenafan.com"
    assert XENAFAN.scheme == "https"
    assert XENAFAN.strip_www is True
    assert XENAFAN.min_delay == 5.0
    assert XENAFAN.max_delay == 10.0


def test_athenaeum_config_values():
    assert ATHENAEUM.host == "xenafiction.net"
    assert ATHENAEUM.scheme == "http"
    assert ATHENAEUM.strip_www is False
    assert ATHENAEUM.extra_headers == {"Cookie": "SUPPRESS_COMMENTS=1"}


def test_default_extra_headers_is_empty():
    assert XENAFAN.extra_headers == {}


def test_academy_config_values():
    assert ACADEMY.host == "academyofbards.org"
    assert ACADEMY.scheme == "https"
    assert ACADEMY.strip_www is False


def test_user_agent_is_built_from_the_given_contact_email():
    assert user_agent_for("researcher@example.org") == "fanfic-metadata-research (researcher@example.org)"


def test_site_configs_carry_no_contact_email():
    for config in (XENAFAN, ATHENAEUM, ACADEMY):
        assert not hasattr(config, "user_agent")
