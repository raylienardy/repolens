from typing import Protocol, Any
from app.analysis.inputs import AnalysisInput

class Analyzer(Protocol):
    def analyze(self, input: AnalysisInput) -> Any:
        ...
