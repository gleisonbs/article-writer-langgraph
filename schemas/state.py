import operator
from typing import Annotated, TypedDict

from .section import Section
from .source import Source


class State(TypedDict):
    topic: str  # the input
    queries: list[str]  # written by plan_research
    sources: list[Source]  # written by web_search
    outline: list[Section]  # written by build_outline
    drafted: Annotated[list[Section], operator.add]  # written by draft_section
    article: str  # written by assemble_article
