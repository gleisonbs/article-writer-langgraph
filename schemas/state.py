import operator
from typing import Annotated, TypedDict

from schemas import Finding, PlannedQuery, Section, Source
from utils import merge_sections


class State(TypedDict):
    topic: str  # the input
    audience: str
    tone: str
    target_words: int
    facets: Annotated[list[str], operator.add]
    queries: list[PlannedQuery]  # written by plan_research
    query_log: Annotated[list[str], operator.add]  # written by plan_research
    research_passes: int
    sources: Annotated[list[Source], operator.add]  # written by web_search
    outline: list[Section]  # written by build_outline
    drafted: Annotated[list[Section], merge_sections]  # written by draft_section
    article: str  # written by assemble_article
    findings: list[Finding]
    scores: Annotated[list[dict], operator.add]
    revision_count: int
