from urllib.parse import urlparse
from app.integrations.github.exceptions import InvalidGitHubUrlError

def parse_github_url(url: str) -> tuple[str, str]:
    """Parse GitHub repository URL into owner and repo.

    Valid: https://github.com/owner/repo, github.com/owner/repo.git,
    owner/repo.
    Invalid: https://gitlab.com/owner/repo, github.com/owner, owner.
    """
    value = url.strip()
    if not value:
        raise InvalidGitHubUrlError("GitHub URL cannot be empty")

    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    if parsed.netloc.lower() != "github.com":
        if "://" not in value and len(value.split("/")) == 2:
            parts = value.split("/")
            owner, repo = parts
        else:
            raise InvalidGitHubUrlError("URL must point to github.com")
    else:
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 2:
            raise InvalidGitHubUrlError("GitHub URL must contain owner and repository")
        owner, repo = parts

    repo = repo.removesuffix(".git")
    if not owner or not repo or any(char in owner + repo for char in "?#"):
        raise InvalidGitHubUrlError("Invalid GitHub owner or repository")
    return owner, repo
