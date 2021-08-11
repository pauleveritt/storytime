"""Promote component-driven-development with a browseable catalog.

Storytime is a system for component-driven-development (CDD.)
You write stories as you develop components, expressing all the variations.
You can then browse them in a web page, as well as use these stories in testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from importlib import import_module
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from inspect import getmembers
from inspect import isfunction
from pathlib import Path
from types import ModuleType
from typing import get_type_hints
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from hopscotch import Registry

if TYPE_CHECKING:
    from .story import Story


def make_target_path(target_module: str) -> Path:
    """Convert the module at ``target_module`` to a full ``Path``.

    Called from the CLI handler to construct a place to look.

    Args:
        target_module: A string with the module where the stories are.

    Returns:
        A ``pathlib.Path`` that is fully-expanded.

    Raises:
        ModuleNotFoundError: The ``target_module`` doesn't point to valid package.
    """
    try:
        module_root = import_module(target_module)
    except ModuleNotFoundError:
        # Re-raise but with a nicer error message
        msg = f"{target_module} is not a package in this environment."
        raise ModuleNotFoundError(msg)
    module_path = Path(module_root.__file__)
    if module_path.name == "__init__.py":
        # This is a package, return parent
        return module_path.parent
    return Path(module_path)


def import_stories(stories_path: Path) -> ModuleType:
    """Given a full path to a stories file, import and return the module."""
    spec = spec_from_file_location(stories_path.name, stories_path)
    if spec is None:
        # No module at that path
        msg = f"No stories file at {stories_path}"
        raise ModuleNotFoundError(msg)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module


def get_certain_callable(module: ModuleType) -> Optional[Union[Section, Subject]]:
    """Return the first Section/Subject in given module that returns correct type.

    A ``stories.py`` file should have a function that, when called,
    constructs an instance of a Section, Subject, etc. This helper
    function does the locating and construction. If no function
    is found with the correct return value, return None.

    We do it this way instead of magically-named functions, meaning,
    we don't do convention over configuration.

    Args:
        module: A stories.py module that should have the right function.

    Returns:
        The Section/Story instance or ``None`` if there wasn't an
        appropriate function.
    """
    valid_returns = (Section, Subject)
    for _name, obj in getmembers(module):
        if isfunction(obj):
            th = get_type_hints(obj)
            return_type = th.get("return")
            if return_type and return_type in valid_returns:
                # Call the obj to let it construct and return the
                # Section/Subject
                target: Union[Section, Subject] = obj()
                return target

    # We didn't find an appropriate callable
    return None


@dataclass()
class Site:
    """The top of a Storytime catalog.

    The site contains the organized collections of stories, with
    logic to render to disk.
    """

    target: Path
    registry: Registry = field(default_factory=Registry)
    tree: dict[Section, list[Subject]] = field(default_factory=dict)

    def add_section(self, section: Section) -> Section:
        """Add a section to the tree while updating defaults from parent."""
        if section not in self.tree:
            self.tree[section] = []
        acquired_attrs = ("registry",)
        for acquired_attr in acquired_attrs:
            if not getattr(section, acquired_attr, False):
                self_attr = getattr(self, acquired_attr)
                setattr(section, acquired_attr, self_attr)
        return section

    def make_sections(self) -> None:
        """Crawl the first level of directories to get each ``Section``."""
        # Get the first level of directories at the path
        for stories_path in self.target.glob("*/stories.py"):
            # Import the module and try to get Section
            module = import_stories(stories_path)
            section = get_certain_callable(module)
            if section and isinstance(section, Section):
                section.make_subjects()
                self.add_section(section)
        return


@dataclass(unsafe_hash=True)
class Section:
    """A grouping of stories, such as ``Views``."""

    title: str
    section_path: Path
    registry: Optional[Registry] = None
    subjects: dict[Subject, list[Subject]] = field(default_factory=dict, hash=False)

    def make_subjects(self) -> None:
        """From this directory, look for ``stories.py`` in subdirs."""
        # Get the first level of directories at the path
        for stories_path in self.section_path.glob("*/stories.py"):
            # Import the module and try to get Section
            module = import_stories(stories_path)
            subject = get_certain_callable(module)
            if subject and isinstance(subject, Subject):
                self.subjects[subject] = []


@dataclass(frozen=True)
class Subject:
    """The component that a group of stories or variants is about."""

    title: str
    subject_path: Path
    registry: Optional[Registry] = None
    stories: list[Story] = field(default_factory=list, hash=False)
