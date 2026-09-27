import base64
from collections.abc import Mapping
import httpx

from app.integrations.github.constants import (
    GITHUB_API_BASE,
    GITHUB_API_TIMEOUT_SECONDS,
    MAX_FILE_SIZE_BYTES,
    MAX_REPOSITORY_SIZE_KB,
    MAX_TREE_ENTRIES,
)
from app.integrations.github.exceptions import (
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
    RepositoryPrivateError,
    RepositoryTooLargeError,
)
from app.integrations.github.schemas import FileContent, RepositoryMetadata, TreeEntry, TreeResponse

class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = GITHUB_API_TIMEOUT_SECONDS):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RepoLens/0.1",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.AsyncClient(base_url=GITHUB_API_BASE, headers=headers, timeout=timeout)

    async def _handle_response(self, resp: httpx.Response) -> Mapping:
        if resp.status_code == 404:
            raise RepositoryNotFoundError("GitHub repository or resource not found")
        if resp.status_code == 403:
            message = resp.text.lower()
            if "rate limit" in message or resp.headers.get("x-ratelimit-remaining") == "0":
                reset_at = int(resp.headers.get("x-ratelimit-reset", "0"))
                raise RateLimitError(reset_at=reset_at)
        if resp.status_code >= 400:
            raise GitHubAPIError(f"GitHub API returned HTTP {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except ValueError as exc:
            raise GitHubAPIError("GitHub API returned invalid JSON") from exc

    async def get_repository(self, owner: str, repo: str) -> RepositoryMetadata:
        resp = await self.client.get(f"/repos/{owner}/{repo}")
        data = await self._handle_response(resp)
        if data.get("private"):
            raise RepositoryPrivateError("Repository is private")
        if data.get("size", 0) > MAX_REPOSITORY_SIZE_KB:
            raise RepositoryTooLargeError("Repository exceeds maximum allowed size")
        license_data = data.get("license")
        return RepositoryMetadata(
            name=data["name"], full_name=data["full_name"], owner=data["owner"]["login"],
            description=data.get("description"), default_branch=data["default_branch"],
            size=data["size"], stars=data["stargazers_count"], forks=data["forks_count"],
            open_issues=data["open_issues_count"], language=data.get("language"),
            languages_url=data["languages_url"], license=license_data.get("spdx_id") if license_data else None,
            is_private=data["private"], html_url=data["html_url"], created_at=data["created_at"],
            updated_at=data["updated_at"], pushed_at=data["pushed_at"],
        )

    async def get_tree(self, owner: str, repo: str, ref: str) -> TreeResponse:
        resp = await self.client.get(f"/repos/{owner}/{repo}/git/trees/{ref}", params={"recursive": "1"})
        data = await self._handle_response(resp)
        raw_entries = data.get("tree", [])
        truncated = bool(data.get("truncated")) or len(raw_entries) > MAX_TREE_ENTRIES
        entries = [TreeEntry.model_validate(entry) for entry in raw_entries[:MAX_TREE_ENTRIES]]
        return TreeResponse(entries=entries, truncated=truncated, sha=data["sha"])

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> FileContent:
        resp = await self.client.get(f"/repos/{owner}/{repo}/contents/{path}", params={"ref": ref})
        data = await self._handle_response(resp)
        size = int(data.get("size", 0))
        if size > MAX_FILE_SIZE_BYTES:
            raise GitHubAPIError(f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes")
        if data.get("encoding") != "base64":
            raise GitHubAPIError("GitHub file content is not base64 encoded")
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
        except (KeyError, ValueError, UnicodeDecodeError) as exc:
            raise GitHubAPIError("Unable to decode GitHub file content") from exc
        return FileContent(path=data.get("path", path), content=content, size=size, encoding=data["encoding"])

    async def close(self):
        await self.client.aclose()
