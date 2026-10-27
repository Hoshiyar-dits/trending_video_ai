from pydantic import BaseModel, ConfigDict

class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    url: str
    source: str
    summary: str
    score: float
