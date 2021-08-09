"""The ``Site`` is the top of the Storytime catalog."""
import pytest

from storytime import get_certain_callable
from storytime import import_stories
from storytime import make_target_path
from storytime import Site
from storytime import Subject


def test_target_path_package() -> None:
    """Ensure that a package path exists and is stored."""
    result = make_target_path("examples.minimal")
    assert result.name == "minimal"


def test_target_path_module() -> None:
    """Ensure that a module path exists and is stored."""
    result = make_target_path("examples.minimal.components.stories")
    assert result.name == "stories.py"


def test_import_stories_success() -> None:
    """Able to import a module at a path."""
    stories_path = make_target_path("examples.minimal.components.stories")
    module = import_stories(stories_path)
    assert module.__name__ == "stories.py"


def test_target_path_not_exist() -> None:
    """Try to get a package that does not exist."""
    with pytest.raises(ModuleNotFoundError) as exc:
        make_target_path("examples.not.exist")
    expected = "examples.not.exist is not a package in this environment."
    assert exc.value.args[0] == expected


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


def test_site_construction() -> None:
    """Make sure a ``Site`` gets constructed with empty tree."""
    target_path = make_target_path("examples.minimal")
    site = Site(target_path)
    assert site.tree == {}


def test_site_collect_sections() -> None:
    """Point the site at the first level of sections and fill tree."""
    target = make_target_path("examples.minimal")
    site = Site(target=target)
    site.make_sections()
    first_section = list(site.tree.keys())[0]
    assert first_section.title == "Components"


def test_section_construction() -> None:
    """Get a section from the examples and see if it looks right."""
    from examples.minimal.components.stories import this_section

    section = this_section()
    assert section.title == "Components"
    assert section.section_path.name == "components"
    assert section.subjects == {}


def test_section_make_subjects() -> None:
    """Look for component stories in a section."""
    from examples.minimal.components.stories import this_section

    section = this_section()
    section.make_subjects()
    first_subject = list(section.subjects.keys())[0]
    assert isinstance(first_subject, Subject)
    assert first_subject.title == "Heading"
    assert first_subject.stories[0].title == "Default Heading"
