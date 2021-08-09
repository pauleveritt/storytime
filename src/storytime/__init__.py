"""Promote component-driven-development with a browseable catalog.

Storytime is a system for component-driven-development (CDD.)
You write stories as you develop components, expressing all the variations.
You can then browse them in a web page, as well as use these stories in testing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path


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


@dataclass()
class Site:
    """The top of a Storytime catalog.

    The site contains the organized collections of stories, with
    logic to render to disk.
    """

    target: Path
    tree: dict[Section: list[Subject]] = field(default_factory=dict)


@dataclass()
class Section:
    """A grouping of stories, such as ``Views``."""

    title: str
    subject: Subject


@dataclass()
class Subject:
    """The component that a group of stories or variants is about."""

    title: str
