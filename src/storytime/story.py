"""A Storytime story has all the information for viewing and testing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from viewdom.render import VDOM


@dataclass(frozen=True)
class Story:
    """The actual contents of an actual story."""

    title: str
    template: Optional[VDOM] = None
