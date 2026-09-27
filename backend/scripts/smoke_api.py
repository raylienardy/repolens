import os
os.environ["AI_PROVIDER"] = "mock"

import asyncio
import sys

sys.path.insert(0, ".")

import httpx

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
settings.AI_PROVIDER = "mock"

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


mock_github_transport = httpx.MockTransport(mock_github_handler)


def _mock_github_init(self, token=None, timeout=30):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "RepoLens/0.1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    self.client = httpx.AsyncClient(
        base_url="https://api.github.com",
        headers=headers,
        timeout=timeout,
        transport=mock_github_transport,
    )


GitHubClient.__init__ = _mock_github_init

from app.db.session import get_db
from app.main import app

engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post("/api/v1/analyze", json={"repo_url": "https://github.com/acme/sample-repo"})
        print("1. POST /api/v1/analyze valid ->", r1.status_code)
        assert r1.status_code == 200, f"scenario 1 expected 200, got {r1.status_code}: {r1.text}"
        body1 = r1.json()
        assert body1.get("from_cache") is False, f"scenario 1 expected from_cache=False, got {body1.get('from_cache')}"

        r2 = await client.post("/api/v1/analyze", json={})
        print("2. POST /api/v1/analyze empty ->", r2.status_code)
        assert r2.status_code == 422, f"scenario 2 expected 422, got {r2.status_code}: {r2.text}"

        r3 = await client.post("/api/v1/analyze", json={"repo_url": "https://gitlab.com/x/y"})
        print("3. POST /api/v1/analyze gitlab ->", r3.status_code)
        assert r3.status_code == 422, f"scenario 3 expected 422, got {r3.status_code}: {r3.text}"

        r4 = await client.get("/api/v1/health")
        print("4. GET /api/v1/health ->", r4.status_code)
        assert r4.status_code == 200, f"scenario 4 expected 200, got {r4.status_code}: {r4.text}"

    await engine.dispose()
    print("ALL PASSED")


if __name__ == "__main__":
    asyncio.run(main())
