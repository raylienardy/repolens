import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.services.orchestrator import orchestrate_analysis
from app.ai.schemas import AIResult

@pytest.mark.asyncio
async def test_orchestrator_full_flow(mock_github_client):
    repo_url = "https://github.com/acme/sample-repo"
    res = await orchestrate_analysis(repo_url, github_client=mock_github_client)
    
    assert res.repo_full_name == "acme/sample-repo"
    assert res.from_cache is False
    assert res.analysis.structure.total_files > 0
    assert res.ai.status == "ok"
    await mock_github_client.close()

@pytest.mark.asyncio
async def test_orchestrator_cache_hit(mock_github_client, db_session):
    repo_url = "https://github.com/acme/sample-repo"
    
    # Call 1: Miss
    r1 = await orchestrate_analysis(repo_url, github_client=mock_github_client, session=db_session)
    assert r1.from_cache is False
    
    # Call 2: Hit
    r2 = await orchestrate_analysis(repo_url, github_client=mock_github_client, session=db_session)
    assert r2.from_cache is True
    await mock_github_client.close()

@pytest.mark.asyncio
async def test_orchestrator_ai_error_graceful(mock_github_client, monkeypatch):
    repo_url = "https://github.com/acme/sample-repo"
    
    mock_provider = MagicMock(spec=["name", "model", "generate_explanation"])
    mock_provider.name = "mock_failing"
    mock_provider.model = "none"
    async def mock_fail(*args, **kwargs):
        raise RuntimeError("AI service is down")
    mock_provider.generate_explanation.side_effect = mock_fail
    
    import app.services.orchestrator as orch
    monkeypatch.setattr(orch, "get_provider", lambda: mock_provider)
    
    res = await orchestrate_analysis(repo_url, github_client=mock_github_client)
    assert res.repo_full_name == "acme/sample-repo"
    assert res.ai.status == "error"
    assert res.analysis.structure.total_files > 0
    await mock_github_client.close()
