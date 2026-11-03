import pytest

from fanfic_scraper.fetch.contact import (
    ENV_VAR, MissingContactEmail, resolve_contact_email, validate_contact_email,
)


def test_environment_variable_is_used_without_prompting():
    def prompt(_):
        raise AssertionError("should not prompt")

    assert resolve_contact_email(prompt, {ENV_VAR: "researcher@example.org"}) == "researcher@example.org"


def test_prompts_when_the_environment_variable_is_unset():
    assert resolve_contact_email(lambda _: " researcher@example.org ", {}) == "researcher@example.org"


@pytest.mark.parametrize("error", [EOFError, NotImplementedError])
def test_no_terminal_to_prompt_on_raises_with_instructions(error):
    def prompt(_):
        raise error

    with pytest.raises(MissingContactEmail, match=ENV_VAR):
        resolve_contact_email(prompt, {})


@pytest.mark.parametrize("value", ["", None, "   ", "not-an-email", "a@b", "two words@example.org"])
def test_unusable_addresses_are_rejected(value):
    with pytest.raises(MissingContactEmail):
        validate_contact_email(value)
