from pydantic import BaseModel


class Finding(BaseModel):
    section_index: int | None = None
    dimension: str  # citation | structure | length | tone
    severity: str  # block | major | minor
    detail: str
