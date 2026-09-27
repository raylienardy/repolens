import asyncio
import json
import sys
import httpx

sys.path.insert(0, ".")

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models import RepositoryAnalysis  # noqa: F401  (register table for create_all)
from app.integrations.github.client import GitHubClient
from app.services.orchestrator import orchestrate_analysis

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
        
        import base64
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


async def main() -> None:
    # In-memory SQLite untuk test cache
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # GitHub mock
    transport = httpx.MockTransport(mock_github_handler)
    github_client = GitHubClient()
    github_client.client = httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=transport,
    )

    repo_url = f"https://github.com/{MOCK_OWNER}/{MOCK_REPO}"

    # Call 1: cache miss
    async with session_maker() as session:
        r1 = await orchestrate_analysis(repo_url, github_client=github_client, session=session)
    print("=== Call 1 (cache miss) ===")
    print("repo_full_name:", r1.repo_full_name)
    print("commit_sha:", r1.commit_sha)
    print("from_cache:", r1.from_cache)
    print("analysis.structure.total_files:", r1.analysis.structure.total_files)
    print("ai.status:", r1.ai.status)
    assert r1.from_cache is False, f"Call 1 expected from_cache=False, got {r1.from_cache}"

    # Call 2: cache hit
    async with session_maker() as session:
        r2 = await orchestrate_analysis(repo_url, github_client=github_client, session=session)
    print("=== Call 2 (cache hit) ===")
    print("from_cache:", r2.from_cache)
    print("ai.status:", r2.ai.status)
    assert r2.from_cache is True, f"Call 2 expected from_cache=True, got {r2.from_cache}"

    await github_client.close()
    await engine.dispose()
    print("ALL PASSED")


if __name__ == "__main__":
    asyncio.run(main())