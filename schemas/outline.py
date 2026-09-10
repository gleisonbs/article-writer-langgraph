from pydantic import BaseModel, Field

from .section import Section


class Outline(BaseModel):
    sections: list[Section] = Field(min_length=3, max_length=6)
