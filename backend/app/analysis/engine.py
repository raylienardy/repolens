from datetime import datetime, timezone
from app.analysis.schemas import AnalysisResult, RepositoryInfo
from app.analysis.analyzers.languages import analyze_languages
from app.analysis.analyzers.structure import analyze_structure
from app.analysis.analyzers.documentation import analyze_documentation
from app.analysis.analyzers.dependencies import analyze_dependencies
from app.analysis.analyzers.frameworks import analyze_frameworks
from app.analysis.inputs import AnalysisInput

ANALYZER_VERSION = "0.1.0"

def run_analysis(input: AnalysisInput) -> AnalysisResult:
    meta = input.repository_metadata
    repo_info = RepositoryInfo(
        full_name=meta.get("full_name", "unknown"),
        owner=meta.get("owner", "unknown"),
        name=meta.get("name", "unknown"),
        description=meta.get("description"),
        default_branch=meta.get("default_branch", "main"),
        stars=meta.get("stars", 0),
        forks=meta.get("forks", 0),
        license=meta.get("license"),
        html_url=meta.get("html_url", "")
    )

    deps = analyze_dependencies(input)
    fwks = analyze_frameworks(input, deps)

    return AnalysisResult(
        analyzer_version=ANALYZER_VERSION,
        analyzed_at=datetime.now(timezone.utc),
        repository=repo_info,
        languages=analyze_languages(input),
        structure=analyze_structure(input),
        documentation=analyze_documentation(input),
        dependencies=deps,
        frameworks=fwks,
    )
