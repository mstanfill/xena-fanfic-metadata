from dataclasses import dataclass, field

# Product token sent in the User-Agent and matched against robots.txt groups.
AGENT_NAME = "fanfic-metadata-research"


def user_agent_for(contact_email: str) -> str:
    return f"{AGENT_NAME} ({contact_email})"


@dataclass(frozen=True)
class SiteConfig:
    name: str
    host: str
    scheme: str = "https"
    strip_www: bool = True
    min_delay: float = 5.0
    max_delay: float = 10.0
    extra_headers: dict = field(default_factory=dict)


XENAFAN = SiteConfig(name="xenafan", host="xenafan.com")
ATHENAEUM = SiteConfig(
    name="athenaeum", host="xenafiction.net", scheme="http", strip_www=False,
    extra_headers={"Cookie": "SUPPRESS_COMMENTS=1"},
)
ACADEMY = SiteConfig(name="academy", host="academyofbards.org", strip_www=False)
