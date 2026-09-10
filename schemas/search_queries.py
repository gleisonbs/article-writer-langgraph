from pydantic import BaseModel, Field


class SearchQueries(BaseModel):
    queries: list[str] = Field(
        description="web search queries that together cover the topic",
        min_length=3,
        max_length=6,
    )
