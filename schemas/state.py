import operator
from typing import Annotated, TypedDict

from schemas import PlannedQuery, Section, Source


class State(TypedDict):
    topic: str  # the input
    audience: str
    facets: Annotated[list[str], operator.add]
    queries: list[PlannedQuery]  # written by plan_research
    query_log: Annotated[list[str], operator.add]  # written by plan_research
    research_passes: int
    sources: list[Source]  # written by web_search
    outline: list[Section]  # written by build_outline
    drafted: Annotated[list[Section], operator.add]  # written by draft_section
    article: str  # written by assemble_article
