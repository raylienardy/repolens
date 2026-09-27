import json
import re
from pathlib import PurePosixPath
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import DependenciesInfo

def _parse_req_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # strip inline comments
    if " #" in line:
        line = line.split(" #", 1)[0].strip()
    
    # regex to match dependency name and specifier
    # e.g., fastapi>=0.100, uvicorn[standard]==0.30.0, sqlalchemy
    match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:\[[^\]]*\])?(.*)$", line)
    if match:
        name = match.group(1).lower()
        version = match.group(2).strip()
        return name, version or "*"
    return None

def analyze_dependencies(input: AnalysisInput) -> DependenciesInfo:
    manifest_files: list[str] = []
    ecosystems: set[str] = set()
    runtime_deps: dict[str, str] = {}
    dev_deps: dict[str, str] = {}

    # Identify manifest files from tree_entries
    known_manifests = {
        "package.json": "nodejs",
        "pyproject.toml": "python",
        "requirements.txt": "python",
        "pipfile": "python",
        "go.mod": "go",
        "cargo.toml": "rust",
        "composer.json": "php",
    }

    for entry in input.tree_entries:
        path = entry.get("path", "")
        filename = PurePosixPath(path).name.lower()
        if filename in known_manifests:
            manifest_files.append(path)
            ecosystems.add(known_manifests[filename])

    # Parse contents available in input.file_contents
    for path, content in input.file_contents.items():
        filename = PurePosixPath(path).name.lower()
        
        try:
            if filename == "package.json":
                ecosystems.add("nodejs")
                if path not in manifest_files:
                    manifest_files.append(path)
                data = json.loads(content)
                for k, v in data.get("dependencies", {}).items():
                    runtime_deps[k.lower()] = str(v)
                for k, v in data.get("devDependencies", {}).items():
                    dev_deps[k.lower()] = str(v)

            elif filename == "composer.json":
                ecosystems.add("php")
                if path not in manifest_files:
                    manifest_files.append(path)
                data = json.loads(content)
                for k, v in data.get("require", {}).items():
                    runtime_deps[k.lower()] = str(v)
                for k, v in data.get("require-dev", {}).items():
                    dev_deps[k.lower()] = str(v)

            elif filename == "pyproject.toml":
                ecosystems.add("python")
                if path not in manifest_files:
                    manifest_files.append(path)
                data = tomllib.loads(content)
                # PEP 621: [project.dependencies]
                project = data.get("project", {})
                for dep in project.get("dependencies", []):
                    parsed = _parse_req_line(dep)
                    if parsed:
                        runtime_deps[parsed[0]] = parsed[1]
                for group, items in project.get("optional-dependencies", {}).items():
                    for dep in items:
                        parsed = _parse_req_line(dep)
                        if parsed:
                            dev_deps[parsed[0]] = parsed[1]

                # Poetry: [tool.poetry.dependencies]
                poetry = data.get("tool", {}).get("poetry", {})
                for k, v in poetry.get("dependencies", {}).items():
                    if k.lower() != "python":
                        runtime_deps[k.lower()] = str(v)
                # Poetry dev dependencies
                for k, v in poetry.get("dev-dependencies", {}).items():
                    dev_deps[k.lower()] = str(v)
                for group, gdata in poetry.get("group", {}).items():
                    for k, v in gdata.get("dependencies", {}).items():
                        dev_deps[k.lower()] = str(v)

            elif filename == "requirements.txt" or filename.endswith(".txt") and "requirements" in filename:
                ecosystems.add("python")
                if path not in manifest_files:
                    manifest_files.append(path)
                for line in content.splitlines():
                    parsed = _parse_req_line(line)
                    if parsed:
                        runtime_deps[parsed[0]] = parsed[1]

            elif filename == "pipfile":
                ecosystems.add("python")
                if path not in manifest_files:
                    manifest_files.append(path)
                data = tomllib.loads(content)
                for k, v in data.get("packages", {}).items():
                    runtime_deps[k.lower()] = str(v)
                for k, v in data.get("dev-packages", {}).items():
                    dev_deps[k.lower()] = str(v)

            elif filename == "cargo.toml":
                ecosystems.add("rust")
                if path not in manifest_files:
                    manifest_files.append(path)
                data = tomllib.loads(content)
                for k, v in data.get("dependencies", {}).items():
                    runtime_deps[k.lower()] = str(v)
                for k, v in data.get("dev-dependencies", {}).items():
                    dev_deps[k.lower()] = str(v)

            elif filename == "go.mod":
                ecosystems.add("go")
                if path not in manifest_files:
                    manifest_files.append(path)
                in_require_block = False
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("require ("):
                        in_require_block = True
                        continue
                    if in_require_block:
                        if line.startswith(")"):
                            in_require_block = False
                            continue
                        parts = line.split()
                        if len(parts) >= 2:
                            runtime_deps[parts[0].lower()] = parts[1]
                    elif line.startswith("require ") and not line.startswith("require ("):
                        parts = line[len("require "):].strip().split()
                        if len(parts) >= 2:
                            runtime_deps[parts[0].lower()] = parts[1]

        except Exception:
            # Graceful error handling: skip corrupted manifest file
            pass

    has_manifest = len(manifest_files) > 0
    total_count = len(runtime_deps) + len(dev_deps)

    return DependenciesInfo(
        has_manifest=has_manifest,
        manifest_files=manifest_files,
        ecosystems=sorted(list(ecosystems)),
        runtime_dependencies=runtime_deps,
        dev_dependencies=dev_deps,
        total_count=total_count,
    )
