import pytest
from app.ai.providers.mock import MockProvider
from app.analysis.inputs import AnalysisInput
from app.analysis.engine import run_analysis
from app.ai.prompts import build_explanation_prompt

@pytest.mark.asyncio
async def test_mock_provider_generate_explanation():
    provider = MockProvider()
    
    # Setup standard analysis result
    metadata = {
        "full_name": "acme/sample-repo",
        "owner": "acme",
        "name": "sample-repo",
        "description": "A sample repository",
        "default_branch": "main",
        "stars": 10,
        "forks": 2,
        "license": "MIT",
        "html_url": "https://github.com/acme/sample-repo"
    }
    tree = [
        {"path": "README.md", "type": "blob", "sha": "1", "size": 10},
        {"path": "pyproject.toml", "type": "blob", "sha": "2", "size": 20},
    ]
    file_contents = {"README.md": "# Sample"}
    
    input_data = AnalysisInput.from_dicts(metadata, tree, file_contents)
    analysis = run_analysis(input_data)
    prompt = build_explanation_prompt(analysis)
    
    res1 = await provider.generate_explanation(analysis, prompt)
    
    # Assertions
    assert res1.status == "ok"
    assert res1.explanation is not None
    assert len(res1.explanation.summary) > 0
    assert res1.explanation.purpose is not None
    assert isinstance(res1.explanation.key_technologies, list)
    
    # Deterministic test
    res2 = await provider.generate_explanation(analysis, prompt)
    assert res1.explanation.model_dump() == res2.explanation.model_dump()
    assert res1.status == res2.status
    assert res1.provider == res2.provider
    assert res1.model == res2.model
