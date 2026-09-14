from pydantic import BaseModel, Field


class Lapse(BaseModel):
    quote: str = Field(
        description="verbatim span from the article that breaks the register"
    )
    why: str


class Verdict(BaseModel):
    wrong_register: bool = Field(
        description="the register is wrong throughout, rather than in specific places"
    )
    lapses: list[Lapse]
