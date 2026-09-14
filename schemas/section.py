from pydantic import BaseModel, Field


class Section(BaseModel):
    index: int
    heading: str
    goal: str = Field(description="what this section must accomplish")
    source_ids: list[int] = Field(description="ids of sources this section needs")
    draft: str = ""  # written by draft_section
    target_words: int
