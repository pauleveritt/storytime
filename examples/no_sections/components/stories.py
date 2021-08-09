"""A stories module which does not correctly export stories."""
from storytime import Section


def make_title() -> str:
    """Make sure the sniffer doesn't break."""
    return "Components"


# We intentionally don't want a return type.
def no_stories():  # type: ignore
    """No type hint on return value, so not used."""
    return Section(title=make_title())
