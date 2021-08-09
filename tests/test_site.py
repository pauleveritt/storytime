"""The ``Site`` is the top of the Storytime catalog."""

import pytest

from storytime import make_target_path, Site


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
