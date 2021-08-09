"""A stories module which does not correctly export stories."""
from storytime import Section


def not_used() -> int:
    """Make sure the sniffer doesn't break."""
    return 99


# We intentionally don't want a return type.
def no_stories():  # type: ignore
    """No type hint on return value, so not used."""
    return Section(title="Components")
