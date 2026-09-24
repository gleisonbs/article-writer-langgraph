from pydantic import BaseModel, Field


class ArticleRequest(BaseModel):
    topic: str = ""
    audience: str = "a technical reader"
    tone: str = "clear and direct"
    target_words: int = Field(default=800, gt=0)
