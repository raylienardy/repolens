from pathlib import PurePosixPath
from app.integrations.github.constants import (
    ENTRY_POINT_PATTERNS,
    PRIORITY_PATTERNS_HIGH,
    PRIORITY_PATTERNS_MEDIUM,
    TEST_FILE_HINTS,
)
from app.integrations.github.schemas import TreeEntry

def classify_file(path: str) -> str:
    normalized = path.lower()
    name = PurePosixPath(normalized).name
    if name in PRIORITY_PATTERNS_HIGH or name in ENTRY_POINT_PATTERNS:
        return "high"
    if any(hint in normalized for hint in TEST_FILE_HINTS):
        return "high"
    if name in PRIORITY_PATTERNS_MEDIUM:
        return "medium"
    return "low"

def select_priority_files(entries: list[TreeEntry], max_count: int) -> list[TreeEntry]:
    blobs = [entry for entry in entries if entry.type == "blob"]
    priority = {"high": 0, "medium": 1, "low": 2}
    return sorted(blobs, key=lambda entry: (priority[classify_file(entry.path)], entry.path.lower()))[:max_count]
