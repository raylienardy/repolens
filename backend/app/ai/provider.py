from typing import Protocol, runtime_checkable
from app.ai.schemas import AIResult
from app.analysis.schemas import AnalysisResult

@runtime_checkable
class AIProvider(Protocol):
    name: str

    async def generate_explanation(
        self, analysis: AnalysisResult, prompt: str
    ) -> AIResult:
        ...
