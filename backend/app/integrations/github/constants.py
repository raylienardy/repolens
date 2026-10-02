MAX_TREE_ENTRIES = 15000
MAX_FILE_SIZE_BYTES = 100 * 1024
MAX_TOTAL_CONTENT_BYTES = 500 * 1024
MAX_REPOSITORY_SIZE_KB = 100 * 1024
MAX_FILES_TO_AI = 20
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_TIMEOUT_SECONDS = 30

PRIORITY_PATTERNS_HIGH = [
    "readme.md", "readme.rst", "readme.txt",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "pyproject.toml", "pipfile", "poetry.lock",
    "composer.json", "pom.xml", "build.gradle", "go.mod", "cargo.toml",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "tsconfig.json", "next.config.js", "next.config.ts",
    "vite.config.js", "vite.config.ts",
]

PRIORITY_PATTERNS_MEDIUM = [
    ".env.example", "makefile", ".editorconfig", ".gitignore", "mkdocs.yml",
    ".eslintrc", ".prettierrc", "webpack.config.js", "babel.config.js",
]

ENTRY_POINT_PATTERNS = [
    "manage.py",
    "main.py", "app.py", "index.ts", "index.js", "main.ts", "main.js",
]

TEST_FILE_HINTS = ["test_", "_test", ".test.", ".spec.", "conftest.py", "tests/"]
