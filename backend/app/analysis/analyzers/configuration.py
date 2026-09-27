from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import ConfigurationInfo

def analyze_configuration(input: AnalysisInput) -> ConfigurationInfo:
    config_files: list[str] = []
    has_docker = False
    has_docker_compose = False
    has_ci = False
    has_env_example = False
    has_makefile = False

    known_configs = {
        ".env.example", ".editorconfig", ".prettierrc", ".eslintrc",
        ".eslintrc.json", ".eslintrc.js", "tsconfig.json", "next.config.js",
        "next.config.ts", "vite.config.ts", "vite.config.js", "makefile",
        "mkdocs.yml", ".flake8", "ruff.toml", "tox.ini"
    }

    for entry in input.tree_entries:
        path = entry.get("path", "")
        norm_path = path.lower()
        filename = PurePosixPath(norm_path).name

        if filename in known_configs:
            config_files.append(entry.get("path", ""))

        if filename in {"dockerfile"}:
            has_docker = True

        if filename in {"docker-compose.yml", "docker-compose.yaml"}:
            has_docker_compose = True

        if norm_path.startswith(".github/workflows/"):
            has_ci = True

        if filename == ".env.example":
            has_env_example = True

        if filename == "makefile":
            has_makefile = True

    return ConfigurationInfo(
        config_files=config_files,
        has_docker=has_docker,
        has_docker_compose=has_docker_compose,
        has_ci=has_ci,
        has_env_example=has_env_example,
        has_makefile=has_makefile,
    )
