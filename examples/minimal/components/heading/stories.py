"""The subject for this Heading component."""
from pathlib import Path

from storytime import Subject
from storytime.story import Story


def this_subject() -> Subject:
    """Let's make a Storytime subject for this Heading component."""
    return Subject(
        title="Heading",
        subject_path=Path(__file__).parent,
        stories=[
            Story(
                title="Default Heading",
            )
        ],
    )
