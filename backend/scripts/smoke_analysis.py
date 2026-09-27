import sys
import json

sys.path.insert(0, ".")

from app.analysis.engine import run_analysis
from app.analysis.inputs import AnalysisInput


def print_result(label: str, res) -> None:
    data = res.model_dump()
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(json.dumps({
        "languages": data["languages"],
        "structure": {k: data["structure"][k] for k in ("total_files", "total_directories", "has_docs_folder")},
        "documentation": {k: data["documentation"][k] for k in ("has_readme", "has_license")},
        "dependencies": {k: data["dependencies"][k] for k in ("has_manifest", "ecosystems", "total_count", "runtime_dependencies")},
        "frameworks": data["frameworks"],
    }, indent=2))


def test_empty():
    data = AnalysisInput.from_dicts({"language": None}, [])
    return run_analysis(data)


def test_mock_small():
    meta = {
        "full_name": "test/repo", "owner": "test", "name": "repo",
        "description": "desc", "default_branch": "main",
        "stars": 1, "forks": 0, "license": "MIT", "html_url": "url",
        "language": "Python"
    }
    tree = [
        {"path": "README.md", "type": "blob", "size": 100},
        {"path": "pyproject.toml", "type": "blob", "size": 50},
        {"path": "src/main.py", "type": "blob", "size": 200},
        {"path": "docs", "type": "tree"},
        {"path": "docs/index.md", "type": "blob", "size": 50},
    ]
    return run_analysis(AnalysisInput.from_dicts(meta, tree))


def test_python_with_pyproject():
    meta = {
        "full_name": "me/api", "owner": "me", "name": "api",
        "default_branch": "main", "stars": 0, "forks": 0,
        "license": "MIT", "html_url": "url", "language": "Python"
    }
    tree = [
        {"path": "pyproject.toml", "type": "blob", "size": 300},
        {"path": "app/main.py", "type": "blob", "size": 200},
        {"path": "tests/conftest.py", "type": "blob", "size": 100},
    ]
    pyproject_content = """
[project]
name = "api"
version = "0.1.0"
dependencies = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.22",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
"""
    file_contents = {"pyproject.toml": pyproject_content}
    return run_analysis(AnalysisInput.from_dicts(meta, tree, file_contents))


def test_nodejs_with_package_json():
    meta = {
        "full_name": "me/web", "owner": "me", "name": "web",
        "default_branch": "main", "stars": 0, "forks": 0,
        "license": None, "html_url": "url", "language": "TypeScript"
    }
    tree = [
        {"path": "package.json", "type": "blob", "size": 400},
        {"path": "src/app/page.tsx", "type": "blob", "size": 200},
    ]
    pkg_content = json.dumps({
        "name": "web",
        "dependencies": {"next": "^14.0.0", "react": "^18.0.0", "react-dom": "^18.0.0"},
        "devDependencies": {"vitest": "^1.0.0", "typescript": "^5.0.0"}
    })
    return run_analysis(AnalysisInput.from_dicts(meta, tree, {"package.json": pkg_content}))


def test_requirements_edge():
    meta = {"full_name": "me/x", "owner": "me", "name": "x", "default_branch": "main",
            "stars": 0, "forks": 0, "license": None, "html_url": "url", "language": "Python"}
    tree = [{"path": "requirements.txt", "type": "blob", "size": 80}]
    req_content = "# comment\nfastapi>=0.100\n\nuvicorn[standard]==0.30.0\nsqlalchemy\n"
    return run_analysis(AnalysisInput.from_dicts(meta, tree, {"requirements.txt": req_content}))


if __name__ == "__main__":
    print_result("Test 1: Empty Repo", test_empty())
    print_result("Test 2: Mock Small Repo", test_mock_small())
    print_result("Test 3: Python + pyproject.toml (FastAPI + pytest + SQLAlchemy)", test_python_with_pyproject())
    print_result("Test 4: Node.js + package.json (Next.js + React + Vitest)", test_nodejs_with_package_json())
    print_result("Test 5: requirements.txt edge (comments, blank lines, mixed format)", test_requirements_edge())
