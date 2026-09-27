from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import EntryPoint, EntryPointInfo

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

        # Evidence text builder
        if depth == 1:
            loc_desc = "at repository root"
        else:
            loc_desc = f"in {parts[0]}/ directory"

        kind: str | None = None
        evidence: str | None = None

        # python_main / python_app: main.py, app.py (root or 1 level down: src/, app/, backend/)
        if filename in {"main.py", "app.py"}:
            if depth == 1:
                kind = "python_main" if filename == "main.py" else "python_app"
                evidence = f"found {filename} {loc_desc}"
            elif depth == 2 and parts[0] in {"src", "app", "backend"}:
                kind = "python_main" if filename == "main.py" else "python_app"
                evidence = f"found {filename} {loc_desc}"

        elif filename == "manage.py" and depth <= 2:
            kind = "python_app"
            evidence = f"found Django manage.py {loc_desc}"

        # node_index: index.js, index.ts, main.js, main.ts (root or 1 level down)
        elif filename in {"index.js", "index.ts", "main.js", "main.ts"}:
            if depth <= 3:
                kind = "node_index"
                evidence = f"found {filename} {loc_desc}"

        # go_main: main.go
        elif filename == "main.go":
            kind = "go_main"
            evidence = f"found {filename} {loc_desc}"

        # rust_main: main.rs
        elif filename == "main.rs":
            kind = "rust_main"
            evidence = f"found {filename} {loc_desc}"

        if kind and evidence:
            found.append(EntryPoint(path=raw_path, kind=kind, evidence=evidence))

    # Sort: root files first (depth ascending), then path alphabetically
    found.sort(key=lambda ep: (len(PurePosixPath(ep.path).parts), ep.path.lower()))

    return EntryPointInfo(found=found[:10])
