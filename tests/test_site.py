"""The ``Site`` is the top of the Storytime catalog."""
from pathlib import Path

import pytest
from hopscotch import Registry

from storytime import get_certain_callable
from storytime import import_stories
from storytime import make_target_path
from storytime import Section
from storytime import Site
from storytime import Subject


@pytest.fixture(scope="session")
def minimal() -> Path:
    """Make the path to the minimal examples."""
    p = make_target_path("examples.minimal")
    return p


@pytest.fixture()
def minimal_site(minimal) -> Site:
    """A ``Site`` pointed at target of ``examples.minimal``."""
    s = Site(target=minimal)
    return s


def test_target_path_package(minimal) -> None:
    """Ensure that a package path exists and is stored."""
    assert minimal.name == "minimal"


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


def test_site_construction(minimal_site) -> None:
    """Make sure a ``Site`` gets constructed with empty tree."""
    assert minimal_site.tree == {}


def test_site_collect_sections(minimal_site) -> None:
    """Point the site at the first level of sections and fill tree."""
    minimal_site.make_sections()
    first_section = list(minimal_site.tree.keys())[0]
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


def test_site_add_section_no_registry(minimal, minimal_site) -> None:
    """The ``Section`` doesn't set a registry so get from ``Site``."""
    section_path = minimal / "components"
    section = Section(title="Minimal Section", section_path=section_path)
    updated_section = minimal_site.add_section(section)
    assert updated_section.title == "Minimal Section"
    assert section.registry is minimal_site.registry


def test_site_add_section_has_registry(minimal, minimal_site) -> None:
    """This ``Section`` assigned a registry so don't acquire from ``Site``."""
    section_registry = Registry()
    section_path = minimal / "components"
    section = Section(
        title="Minimal Section",
        section_path=section_path,
        registry=section_registry,
    )
    updated_section = minimal_site.add_section(section)
    assert updated_section.title == "Minimal Section"
    assert section.registry is not minimal_site.registry
