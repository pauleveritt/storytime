"""A Storytime story has all the information for viewing and testing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from viewdom.render import render
from viewdom.render import VDOM


@dataclass(frozen=True)
class Story:
    """The actual contents of an actual story."""

    title: str
    template: Optional[VDOM] = None

    @property
    def html(self) -> BeautifulSoup:
        """Render to a DOM-like BeautifulSoup representation."""
        # if self.registry is None:
        #     rendered = viewdom_render(self.vdom)
        # else:
        #     rendered = viewdom_wired_render(self.vdom, container=self.container)
        rendered = render(self.template)  # type: ignore
        this_html = BeautifulSoup(rendered, "html.parser")
        return this_html
