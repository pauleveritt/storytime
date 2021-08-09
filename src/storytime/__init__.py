"""Promote component-driven-development with a browseable catalog.

Storytime is a system for component-driven-development (CDD.)
You write stories as you develop components, expressing all the variations.
You can then browse them in a web page, as well as use these stories in testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from importlib import import_module
from inspect import getmembers
from inspect import isfunction
from pathlib import Path
from types import ModuleType
from typing import get_type_hints
from typing import Optional
from typing import Union


def make_target_path(target_module: str) -> Path:
    """Convert the module at ``target_module`` to an full ``Path``.

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
    module_path = Path(module_root.__file__).parent
    return Path(module_path)


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
    tree: dict[Section, list[Subject]] = field(default_factory=dict)


@dataclass()
class Section:
    """A grouping of stories, such as ``Views``."""

    title: str


@dataclass()
class Subject:
    """The component that a group of stories or variants is about."""

    title: str
