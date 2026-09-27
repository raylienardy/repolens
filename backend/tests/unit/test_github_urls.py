import pytest
from app.integrations.github.urls import parse_github_url
from app.integrations.github.exceptions import InvalidGitHubUrlError

valid_cases = [
    "https://github.com/owner/repo",
    "https://github.com/owner/repo.git",
    "https://github.com/owner/repo/",
    "github.com/owner/repo",
    "owner/repo",
]

invalid_cases = [
    "https://gitlab.com/owner/repo",
    "not a url",
    "",
]

@pytest.mark.parametrize("url", valid_cases)
def test_parse_github_url_valid(url):
    owner, repo = parse_github_url(url)
    assert owner == "owner"
    assert repo == "repo"

@pytest.mark.parametrize("url", invalid_cases)
def test_parse_github_url_invalid(url):
    with pytest.raises(InvalidGitHubUrlError):
        parse_github_url(url)
