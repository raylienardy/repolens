import asyncio

from app.core.config import settings
from app.integrations.github.client import GitHubClient
from app.integrations.github.selectors import select_priority_files
from app.integrations.github.urls import parse_github_url


async def main() -> None:
    for sample in (
        "https://github.com/tiangolo/fastapi",
        "https://github.com/tiangolo/fastapi.git",
        "tiangolo/fastapi",
    ):
        print("URL_OK:", sample, "->", parse_github_url(sample))

    for sample in ("https://gitlab.com/owner/repo", "github.com/owner", "not a url"):
        try:
            parse_github_url(sample)
            print("URL_UNEXPECTED_PASS:", sample)
        except Exception as exc:
            print("URL_REJECTED:", sample, "->", type(exc).__name__)

    client = GitHubClient(token=settings.GITHUB_TOKEN)
    try:
        owner, repo = parse_github_url("https://github.com/tiangolo/fastapi")
        meta = await client.get_repository(owner, repo)
        print("REPO:", meta.full_name, "| branch:", meta.default_branch, "| size_kb:", meta.size)
        print("REPO_STATS: stars=%s forks=%s language=%s license=%s" % (
            meta.stars, meta.forks, meta.language, meta.license))
        tree = await client.get_tree(owner, repo, meta.default_branch)
        print("TREE: entries=%s truncated=%s" % (len(tree.entries), tree.truncated))
        picked = select_priority_files(tree.entries, 5)
        print("PRIORITY_FILES:", [entry.path for entry in picked])
        target = next((entry for entry in picked if entry.path.lower().endswith("readme.md")), picked[0])
        content = await client.get_file_content(owner, repo, target.path, meta.default_branch)
        print("FILE:", content.path, "| size:", content.size, "| first_line:",
              content.content.splitlines()[0][:80] if content.content else "<empty>")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
