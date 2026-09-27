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
        "testing": data["testing"],
        "configuration": data["configuration"],
        "security_signals": data["security_signals"],
        "entry_points": data["entry_points"],
    }, indent=2))


def base_meta(name="repo", language=None):
    return {
        "full_name": f"test/{name}", "owner": "test", "name": name,
        "description": "desc", "default_branch": "main", "stars": 0,
        "forks": 0, "license": None, "html_url": "url", "language": language,
    }


def test_empty():
    return run_analysis(AnalysisInput.from_dicts(base_meta(language=None), []))


def test_mock_small():
    tree = [
        {"path": "README.md", "type": "blob", "size": 100},
        {"path": "pyproject.toml", "type": "blob", "size": 50},
        {"path": "src/main.py", "type": "blob", "size": 200},
        {"path": "docs", "type": "tree"},
        {"path": "docs/index.md", "type": "blob", "size": 50},
    ]
    return run_analysis(AnalysisInput.from_dicts(base_meta(language="Python"), tree))


def test_python_with_pyproject():
    tree = [
        {"path": "pyproject.toml", "type": "blob", "size": 300},
        {"path": "app/main.py", "type": "blob", "size": 200},
        {"path": "tests/conftest.py", "type": "blob", "size": 100},
    ]
    pyproject_content = """
[project]
name = "api"
version = "0.1.0"
dependencies = ["fastapi>=0.100", "uvicorn[standard]>=0.22", "sqlalchemy>=2.0"]
[project.optional-dependencies]
dev = ["pytest>=7.0"]
"""
    return run_analysis(AnalysisInput.from_dicts(base_meta("api", "Python"), tree, {"pyproject.toml": pyproject_content}))


def test_nodejs_with_package_json():
    tree = [
        {"path": "package.json", "type": "blob", "size": 400},
        {"path": "src/app/page.tsx", "type": "blob", "size": 200},
    ]
    pkg_content = json.dumps({
        "name": "web", "dependencies": {"next": "^14.0.0", "react": "^18.0.0"},
        "devDependencies": {"vitest": "^1.0.0"}
    })
    return run_analysis(AnalysisInput.from_dicts(base_meta("web", "TypeScript"), tree, {"package.json": pkg_content}))


def test_requirements_edge():
    tree = [{"path": "requirements.txt", "type": "blob", "size": 80}]
    req_content = "# comment\nfastapi>=0.100\n\nuvicorn[standard]==0.30.0\nsqlalchemy\n"
    return run_analysis(AnalysisInput.from_dicts(base_meta("requirements", "Python"), tree, {"requirements.txt": req_content}))


def test_testing_signals():
    tree = [
        {"path": "tests", "type": "tree"},
        {"path": "tests/test_a.py", "type": "blob", "size": 10},
        {"path": "tests/test_b.py", "type": "blob", "size": 10},
        {"path": "conftest.py", "type": "blob", "size": 10},
        {"path": "pytest.ini", "type": "blob", "size": 10},
        {"path": ".github/workflows/test.yml", "type": "blob", "size": 10},
    ]
    return run_analysis(AnalysisInput.from_dicts(base_meta("testing", "Python"), tree))


def test_configuration_security():
    tree = [
        {"path": "Dockerfile", "type": "blob", "size": 10},
        {"path": "docker-compose.yml", "type": "blob", "size": 10},
        {"path": "Makefile", "type": "blob", "size": 10},
        {"path": ".env.example", "type": "blob", "size": 10},
        {"path": "SECURITY.md", "type": "blob", "size": 10},
        {"path": ".gitignore", "type": "blob", "size": 10},
        {"path": "LICENSE", "type": "blob", "size": 10},
        {"path": ".github/dependabot.yml", "type": "blob", "size": 10},
    ]
    return run_analysis(AnalysisInput.from_dicts(base_meta("signals"), tree))


def test_entry_points():
    tree = [
        {"path": "backend/main.py", "type": "blob", "size": 10},
        {"path": "frontend/index.ts", "type": "blob", "size": 10},
        {"path": "cli/main.go", "type": "blob", "size": 10},
    ]
    return run_analysis(AnalysisInput.from_dicts(base_meta("entries"), tree))


if __name__ == "__main__":
    tests = [
        ("Test 1: Empty Repo", test_empty),
        ("Test 2: Mock Small Repo", test_mock_small),
        ("Test 3: Python + pyproject.toml", test_python_with_pyproject),
        ("Test 4: Node.js + package.json", test_nodejs_with_package_json),
        ("Test 5: requirements.txt edge", test_requirements_edge),
        ("Test 6: Testing Signals", test_testing_signals),
        ("Test 7: Configuration + Security Signals", test_configuration_security),
        ("Test 8: Entry Points", test_entry_points),
    ]
    for label, test in tests:
        print_result(label, test())
