class GitHubError(Exception):
    pass

class InvalidGitHubUrlError(GitHubError):
    pass

class RepositoryNotFoundError(GitHubError):
    pass

class RepositoryPrivateError(GitHubError):
    pass

class RepositoryTooLargeError(GitHubError):
    pass

class RateLimitError(GitHubError):
    def __init__(self, message: str = "GitHub API rate limit exceeded", reset_at: int = 0):
        super().__init__(message)
        self.reset_at = reset_at

class GitHubAPIError(GitHubError):
    pass
