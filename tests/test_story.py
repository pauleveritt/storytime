"""Ensure all variations of a ``Story`` obey policies."""
from viewdom.render import html

from storytime.story import Story


def test_empty() -> None:
    """The simplest possible story."""
    story = Story(title="Empty")
    assert story.title == "Empty"


def test_template() -> None:
    """The simplest possible *useful* story."""
    template = html("<div>Hello</div>")
    story = Story(title="Template", template=template)
    assert story.template == template
    assert str(story.html) == "<div>Hello</div>"
