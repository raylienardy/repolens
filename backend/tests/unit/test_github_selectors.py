import pytest
from app.integrations.github.selectors import classify_file, select_priority_files
from app.integrations.github.schemas import TreeEntry

def make_entry(path, type="blob"):
    return TreeEntry(path=path, type=type, sha="sha", size=None)

def test_classify_file():
    assert classify_file("README.md") == "high"
    assert classify_file("package.json") == "high"
    assert classify_file("random.txt") == "low"

def test_classify_file_entry_points():
    assert classify_file("src/main.py") == "high"
    assert classify_file("manage.py") == "high"
    assert classify_file("app/index.ts") == "high"

def test_select_priority_files():
    entries = [
        make_entry("a.txt"),
        make_entry("README.md"),
        make_entry("src/main.py"),
        make_entry("package.json"),
    ]
    selected = select_priority_files(entries, max_count=3)
    # high files sorted alphabetically, then low
    assert [e.path for e in selected] == ["README.md", "package.json", "src/main.py"]

