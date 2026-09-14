from pydantic import BaseModel


class PlannedQuery(BaseModel):
    query: str
    facet: str
