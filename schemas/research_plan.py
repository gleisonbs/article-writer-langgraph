from pydantic import BaseModel, Field

from schemas import PlannedQuery


class ResearchPlan(BaseModel):
    facets: list[str] = Field(description="themes this article must cover")
    queries: list[PlannedQuery] = Field(min_length=3, max_length=6)
