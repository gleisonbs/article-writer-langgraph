from pydantic import BaseModel, Field


class PlannedQuery(BaseModel):
    query: str
    facet: str
