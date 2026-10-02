from pathlib import PurePosixPath

from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import EntryPoint, EntryPointInfo


# Folders we never treat as entry point containers.
_EXCLUDED_CONTAINERS = {
    "examples", "example",
    "tests", "test",
    "docs", "doc",
    "scripts", "script",
    "samples", "sample",
}

# Python entry-point filenames -> kind.
_PY_ENTRY_FILES: dict[str, str] = {
    "main.py": "python_main",
    "app.py": "python_app",
    "applications.py": "python_app",
    "__main__.py": "python_main",
    "wsgi.py": "python_wsgi",
    "asgi.py": "python_asgi",
    "manage.py": "python_app",
}

# Node entry-point filenames.
_NODE_ENTRY_FILES = {
    "index.js", "index.ts", "index.mjs", "index.cjs",
    "main.js", "main.ts",
    "server.js", "server.ts",
    "app.js", "app.ts",
}


def analyze_entry_points(input: AnalysisInput) -> EntryPointInfo:
    found: list[EntryPoint] = []

    for entry in input.tree_entries:
        if entry.get("type") != "blob":
            continue

        raw_path = entry.get("path", "")
        norm_path = raw_path.lower()
        parts = PurePosixPath(norm_path).parts
        filename = PurePosixPath(norm_path).name
        depth = len(parts)

        # Skip anything inside containers we never consider.
        if any(p in _EXCLUDED_CONTAINERS for p in parts[:-1]):
            continue

        if depth == 1:
            loc_desc = "at repository root"
        else:
            loc_desc = f"in {'/'.join(parts[:-1])}/"

        kind: str | None = None
        evidence: str | None = None

        # Python: allow up to depth 3 (root, pkg/, src/pkg/).
        if filename in _PY_ENTRY_FILES and depth <= 3:
            kind = _PY_ENTRY_FILES[filename]
            evidence = f"found {filename} {loc_desc}"

        # Node: allow up to depth 3.
        elif filename in _NODE_ENTRY_FILES and depth <= 3:
            kind = "node_index"
            evidence = f"found {filename} {loc_desc}"

        # Go / Rust: keep the shallow rule.
        elif filename == "main.go" and depth <= 2:
            kind = "go_main"
            evidence = f"found {filename} {loc_desc}"

        elif filename == "main.rs" and depth <= 2:
            kind = "rust_main"
            evidence = f"found {filename} {loc_desc}"

        if kind and evidence:
            found.append(EntryPoint(path=raw_path, kind=kind, evidence=evidence))

    # Sort: shallow first, then alphabetical.
    found.sort(key=lambda ep: (len(PurePosixPath(ep.path).parts), ep.path.lower()))
    return EntryPointInfo(found=found[:10])