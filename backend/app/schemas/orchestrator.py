from datetime import datetime
from pydantic import BaseModel

from app.analysis.schemas import AnalysisResult
from app.ai.schemas import AIResult

class AnalysisResponse(BaseModel):
    repo_url: str
    repo_full_name: str
    commit_sha: str
    from_cache: bool
    analyzed_at: datetime
    analysis: AnalysisResult
    ai: AIResult
