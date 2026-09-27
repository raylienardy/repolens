from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    repo_url: str = Field(min_length=1)
