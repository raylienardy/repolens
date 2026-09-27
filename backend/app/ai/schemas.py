from datetime import datetime
from pydantic import BaseModel

class AIExplanation(BaseModel):
    summary: str
    purpose: str
    key_technologies: list[str]
    architecture_notes: str
    notable_findings: list[str]
    improvement_suggestions: list[str]
    inference_disclaimer: str

class AIResult(BaseModel):
    status: str
    provider: str
    model: str | None = None
    explanation: AIExplanation | None = None
    error_message: str | None = None
    generated_at: datetime
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
