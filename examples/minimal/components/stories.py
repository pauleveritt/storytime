"""Minimal examples in the Components section of stories."""
from pathlib import Path

from storytime import Section


def this_section() -> Section:
    """Let's make a Storytime section for Components."""
    return Section(
        title="Components",
        section_path=Path(__file__).parent,
    )
