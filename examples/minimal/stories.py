"""The ``Site`` for the stories in this package."""
from storytime import Site


def this_site() -> Site:
    """The top of this package's story catalog."""
    return Site(
        title="Minimal Site",
    )
