import pytest
from app.analysis.engine import run_analysis
from app.analysis.inputs import AnalysisInput

def test_run_analysis_empty_repo():
    input_data = AnalysisInput.from_dicts(metadata={}, tree_entries=[], file_contents={})
    result = run_analysis(input_data)
    assert result.documentation.has_readme is False
    assert result.dependencies.has_manifest is False

def test_run_analysis_basic_repo():
    tree = [
        {"path": "README.md", "type": "blob", "sha": "1", "size": 10},
        {"path": "pyproject.toml", "type": "blob", "sha": "2", "size": 20},
        {"path": "src/main.py", "type": "blob", "sha": "3", "size": 30},
    ]
    input_data = AnalysisInput.from_dicts(
        metadata={"full_name": "owner/repo", "owner": "owner", "name": "repo", "description": None, "default_branch": "main", "stars": 0, "forks": 0, "license": None, "html_url": ""},
        tree_entries=tree,
        file_contents={}
    )
    result = run_analysis(input_data)
    # languages detection
    assert ".py" in result.languages.detected
    # documentation
    assert result.documentation.has_readme is True
    # dependencies
    assert result.dependencies.has_manifest is True
