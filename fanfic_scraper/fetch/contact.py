"""The contact email sent with every request.

Each person running the scraper must supply their own address, so site
operators can reach whoever is actually crawling. It is read from the
FANFIC_CONTACT_EMAIL environment variable, or asked for interactively the
first time a request is about to be sent. Runs that only read saved pages
never ask.
"""
import os
import re

ENV_VAR = "FANFIC_CONTACT_EMAIL"
_EMAIL_RE = re.compile(r"^[^@\s()]+@[^@\s()]+\.[^@\s()]+$")


class MissingContactEmail(Exception):
    pass


def validate_contact_email(value) -> str:
    email = (value or "").strip()
    if not _EMAIL_RE.match(email):
        raise MissingContactEmail(
            f"{email!r} is not a usable contact email. Set {ENV_VAR}, or pass "
            "contact_email=..., with an address site operators can reach you at."
        )
    return email


def resolve_contact_email(prompt_fn=input, environ=os.environ) -> str:
    """Return the contact email from the environment, or ask for it."""
    if environ.get(ENV_VAR):
        return validate_contact_email(environ[ENV_VAR])
    try:
        answer = prompt_fn(
            "Contact email to include in the User-Agent (site operators may use it "
            f"to reach you; set {ENV_VAR} to skip this prompt): "
        )
    except (EOFError, NotImplementedError):  # no terminal, or a headless notebook kernel
        raise MissingContactEmail(
            f"No contact email: set {ENV_VAR} or pass contact_email=... to the fetcher."
        ) from None
    return validate_contact_email(answer)
