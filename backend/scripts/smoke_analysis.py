from datetime import datetime, timezone
from app.analysis.engine import run_analysis
from app.analysis.inputs import AnalysisInput

def test_empty():
    print("--- Test 1: Empty Repo ---")
    data = AnalysisInput.from_dicts({"language": None}, [])
    res = run_analysis(data)
    print(res.model_dump_json(indent=2))

def test_mock():
    print("\n--- Test 2: Mock Repo ---")
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
        {"path": "docs/index.md", "type": "blob", "size": 50}
    ]
    data = AnalysisInput.from_dicts(meta, tree)
    res = run_analysis(data)
    print(res.model_dump_json(indent=2))

if __name__ == "__main__":
    test_empty()
    test_mock()
