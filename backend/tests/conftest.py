import base64
import pytest
import pytest_asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db.base import Base
from app.db.models import RepositoryAnalysis  # noqa: F401
from app.integrations.github.client import GitHubClient

MOCK_OWNER = "acme"
MOCK_REPO = "sample-repo"
MOCK_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def mock_github_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    
    if f"/repos/{MOCK_OWNER}/{MOCK_REPO}/git/trees/" in url:
        return httpx.Response(
            200,
            json={
                "sha": MOCK_SHA,
                "url": url,
                "tree": [
                    {"path": "README.md", "mode": "100644", "type": "blob", "sha": "1234567890abcdef", "size": 25},
                    {"path": "pyproject.toml", "mode": "100644", "type": "blob", "sha": "abcdef1234567890", "size": 40},
                ],
                "truncated": False,
            },
        )

    if f"/repos/{MOCK_OWNER}/{MOCK_REPO}/contents/" in url:
        if "README.md" in url:
            content_str = "# Sample Repo\nA dummy readme."
        else:
            content_str = '[project]\nname = "sample"\nversion = "0.1.0"\n'
        
        b64_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        path_name = "README.md" if "README.md" in url else "pyproject.toml"
        return httpx.Response(
            200,
            json={
                "name": path_name,
                "path": path_name,
                "sha": "12345",
                "size": len(content_str),
                "encoding": "base64",
                "content": b64_content,
            },
        )

    if f"/repos/{MOCK_OWNER}/{MOCK_REPO}" in url:
        return httpx.Response(
            200,
            json={
                "name": MOCK_REPO,
                "full_name": f"{MOCK_OWNER}/{MOCK_REPO}",
                "owner": {"login": MOCK_OWNER},
                "description": "Mock repo for smoke testing orchestrator",
                "default_branch": "main",
                "size": 100,
                "stargazers_count": 10,
                "forks_count": 2,
                "open_issues_count": 0,
                "language": "Python",
                "languages_url": f"https://api.github.com/repos/{MOCK_OWNER}/{MOCK_REPO}/languages",
                "license": {"spdx_id": "MIT"},
                "private": False,
                "html_url": f"https://github.com/{MOCK_OWNER}/{MOCK_REPO}",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "pushed_at": "2026-01-02T00:00:00Z",
            },
        )

    return httpx.Response(404, json={"message": "Not Found"})

@pytest.fixture
def mock_github_transport():
    return httpx.MockTransport(mock_github_handler)

@pytest.fixture
def mock_github_client(mock_github_transport):
    client = GitHubClient()
    client.client = httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=mock_github_transport,
    )
    return client

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session
        
    await engine.dispose()
