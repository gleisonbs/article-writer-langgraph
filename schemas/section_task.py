from typing import TypedDict

from .section import Section
from .source import Source


class SectionTask(TypedDict):
    section: Section
    headings: list[str]
    sources: list[Source]
    audience: str
    tone: str
    problems: list[str]
