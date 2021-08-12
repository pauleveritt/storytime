"""Promote component-driven-development with a browseable catalog.

Storytime is a system for component-driven-development (CDD.)
You write stories as you develop components, expressing all the variations.
You can then browse them in a web page, as well as use these stories in testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from importlib.resources import files
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from inspect import getmembers
from inspect import isfunction
from pathlib import Path
from types import ModuleType
from typing import cast
from typing import get_type_hints
from typing import Optional
from typing import Union

from hopscotch import Registry


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


def get_certain_callable(module: ModuleType) -> Optional[Union[Site, Section, Subject]]:
    """Return the first Site/Section/Subject in given module that returns correct type.

    A ``stories.py`` file should have a function that, when called,
    constructs an instance of a Section, Subject, etc. This helper
    function does the locating and construction. If no function
    is found with the correct return value, return None.

    We do it this way instead of magically-named functions, meaning,
    we don't do convention over configuration.

    Args:
        module: A stories.py module that should have the right function.

    Returns:
        The Site/Section/Story instance or ``None`` if there wasn't an
        appropriate function.
    """
    valid_returns = (Site, Section, Subject)
    for _name, obj in getmembers(module):
        if isfunction(obj):
            th = get_type_hints(obj)
            return_type = th.get("return")
            if return_type and return_type in valid_returns:
                # Call the obj to let it construct and return the
                # Site/Section/Subject
                target: Union[Site, Section, Subject] = obj()
                return target

    # We didn't find an appropriate callable
    return None


@dataclass()
class TreeNode:
    """Adapt a story path into all info needed to seat in tree.

    Extracting a ``stories.py`` into a tree node is somewhat complicated.
    You have to import the module, convert path to dotted-package-name form,
    find the parent, etc.
    """

    root_path: str
    stories_path: Path
    name: str = field(init=False)
    called_instance: object = field(init=False)
    package_path: str = field(init=False)
    parent_path: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Assign calculated fields."""
        story_module = import_stories(self.stories_path)
        self.called_instance = get_certain_callable(story_module)

        # We want dotted-package-strings for current and parent.
        pure_root_path = cast(Path, files(self.root_path))
        this_package = self.stories_path.parent
        package_path = this_package.relative_to(pure_root_path)
        parent_path = package_path.parent
        if parent_path == package_path:
            # We are at the root stories.py getting a Site
            self.name = ""
            self.parent_path = None
            self.package_path = "."
        else:
            self.name = package_path.name
            self.package_path = f".{package_path}".replace("/", ".")
            self.parent_path = "." if str(parent_path) == "." else f".{parent_path}"


def make_site(target_path: str) -> Site:
    """Create a site with a populated tree.

    This is called from the CLI with a package-name path such
    as ``examples.minimal`` which is the root of a Storytime tree.

    Args:
        target_path: String using dotted package path notation.

    Returns:
        A populated site.
    """
    # Turn the package dotted name of self.target into ``Path``
    root_path = cast(Path, files(target_path))

    # Get all the stories.py under here
    tree_nodes: list[TreeNode] = [
        TreeNode(root_path=target_path, stories_path=stories_path)
        for stories_path in root_path.glob("**/stories.py")
    ]
    # First get the Site
    site: Optional[Site] = None
    for tree_node in tree_nodes:
        if isinstance(tree_node.called_instance, Site):
            site = tree_node.called_instance
            site.post_update(tree_node=tree_node)
    site = cast(Site, site)

    # Now the sections
    for tree_node in tree_nodes:
        section = tree_node.called_instance
        if isinstance(section, Section):
            section.post_update(parent=site, tree_node=tree_node)
            site.items[section.name] = section

    # Now the subjects
    for tree_node in tree_nodes:
        subject = tree_node.called_instance
        if isinstance(subject, Subject):
            # Getting the parent is a little harder here
            if tree_node.parent_path:
                parent = site.find_path(tree_node.parent_path)
                if isinstance(parent, Section):
                    subject.post_update(parent=parent, tree_node=tree_node)
                    parent.items[subject.name] = subject

    return site


@dataclass()
class Site:
    """The top of a Storytime catalog.

    The site contains the organized collections of stories, with
    logic to render to disk.

    Args:
        target: A package string for where to start looking for stories.
    """

    name: str = ""
    parent: None = None
    package_path: str = field(init=False)
    registry: Registry = field(default_factory=Registry)
    title: Optional[str] = None
    items: dict[str, Section] = field(default_factory=dict)

    def post_update(self, tree_node: TreeNode) -> Site:
        """The parent calls this after construction.

        We do this as a convenience, so authors don't have to put a bunch
        of attributes in their stories.

        Args:
            tree_node: The raw data from the scanning process.

        Returns:
            The updated site.
        """
        self.package_path = tree_node.package_path
        if self.title is None:
            self.title = tree_node.package_path

        return self

    def find_path(self, path: str) -> Optional[Union[Site, Section, Subject, Story]]:
        """Given a dotted path, traverse to the object."""
        current = self
        segments = path.split(".")[1:]
        for segment in segments:
            if current is not None:
                current = current.items.get(segment)  # type: ignore
        return current


@dataclass()
class Section:
    """A grouping of stories, such as ``Views``."""

    parent: Site = field(init=False)
    name: str = field(init=False)
    package_path: str = field(init=False)
    registry: Optional[Registry] = None
    title: Optional[str] = None
    items: dict[str, Subject] = field(default_factory=dict)

    def post_update(self, parent: Site, tree_node: TreeNode) -> Section:
        """The parent calls this after construction.

        We do this as a convenience, so authors don't have to put a bunch
        of attributes in their stories.

        Args:
            parent: The Site that is the parent in the tree.
            tree_node: The raw data from the scanning process.

        Returns:
            The updated Section.
        """
        self.parent = parent
        self.name = tree_node.name
        self.package_path = tree_node.package_path
        if self.registry is None:
            self.registry = parent.registry
        if self.title is None:
            self.title = self.package_path
        return self


@dataclass()
class Subject:
    """The component that a group of stories or variants is about."""

    parent: Section = field(init=False)
    name: str = field(init=False)
    package_path: str = field(init=False)
    registry: Optional[Registry] = None
    title: Optional[str] = None
    stories: list[Story] = field(default_factory=list)

    def post_update(self, parent: Section, tree_node: TreeNode) -> Subject:
        """The parent calls this after construction.

        We do this as a convenience, so authors don't have to put a bunch
        of attributes in their stories.

        Args:
            parent: The Section that is the parent in the tree.
            tree_node: The raw data from the scanning process.

        Returns:
            The updated Subject.
        """
        self.parent = parent
        self.name = tree_node.name
        self.package_path = tree_node.package_path
        if self.registry is None:
            self.registry = parent.registry
        if self.title is None:
            self.title = self.package_path
        return self


@dataclass()
class Story:
    """One way to look at a component."""

    parent: Section = field(init=False)
    registry: Optional[Registry] = None
    title: Optional[str] = None

    def post_update(self, parent: Section) -> Story:
        """The parent calls this after construction.

        We do this as a convenience, so authors don't have to put a bunch
        of attributes in their stories.

        Args:
            parent: The Section that is the parent in the tree.

        Returns:
            The updated Story.
        """
        self.parent = parent
        if self.registry is None:
            self.registry = parent.registry
        if self.title is None and self.parent.title:
            self.title = self.parent.title + " Story"
        return self
