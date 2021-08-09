"""The ``Site`` is the top of the Storytime catalog."""
import pytest

from storytime import get_certain_callable
from storytime import make_target_path
from storytime import Site


def test_target_path() -> None:
    """Ensure that the target path exists and is stored."""
    result = make_target_path("examples.minimal")
    assert result.name == "minimal"


def test_target_path_not_exist() -> None:
    """Try to get a package that does not exist."""
    with pytest.raises(ModuleNotFoundError) as exc:
        make_target_path("examples.not.exist")
    expected = "examples.not.exist is not a package in this environment."
    assert exc.value.args[0] == expected


def test_site_construction() -> None:
    """Make sure a ``Site`` gets constructed with empty tree."""
    target_path = make_target_path("examples.minimal")
    site = Site(target_path)
    assert site.tree == {}


def test_get_certain_callable() -> None:
    """Given a module, find the function that returns certain type."""
    from examples.minimal.components import stories

    section = get_certain_callable(stories)
    if section:
        assert section.title == "Components"


def test_no_callable() -> None:
    """This example does not have a function with correct rturn type."""
    from examples.no_sections.components import stories

    section = get_certain_callable(stories)
    assert section is None

