import json
import re
from pathlib import PurePosixPath

from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import (
    DependenciesInfo,
    DetectedFramework,
    FrameworksInfo,
)


def analyze_frameworks(
    input: AnalysisInput, deps: DependenciesInfo
) -> FrameworksInfo:
    detected: list[DetectedFramework] = []

    file_names_lower = {
        PurePosixPath(p).name.lower() for p in input.file_contents.keys()
    }

    def find_evidence_dep(dep_name: str) -> str:
        # Best-effort: point to the manifest file that most likely lists this dep.
        if "package.json" in file_names_lower:
            return "found in package.json"
        if "pyproject.toml" in file_names_lower:
            return "found in pyproject.toml"
        if "requirements.txt" in file_names_lower:
            return "found in requirements.txt"
        if "cargo.toml" in file_names_lower:
            return "found in Cargo.toml"
        if "go.mod" in file_names_lower:
            return "found in go.mod"
        return "found in dependencies"

    def project_self_name() -> tuple[str | None, str | None]:
        """Detect the project's own name from its manifest, if any."""
        for path, content in input.file_contents.items():
            name = PurePosixPath(path).name.lower()
            if name == "pyproject.toml":
                m = re.search(r'^\s*name\s*=\s*"([^"]+)"', content, re.MULTILINE)
                if m:
                    return m.group(1).lower(), "project name in pyproject.toml"
            elif name == "package.json":
                try:
                    data = json.loads(content)
                except (ValueError, TypeError):
                    continue
                n = data.get("name")
                if isinstance(n, str):
                    normalized = n.lower().lstrip("@").split("/")[0]
                    return normalized, "project name in package.json"
        return None, None

    self_name, self_evidence = project_self_name()
    all_deps = {**deps.runtime_dependencies, **deps.dev_dependencies}

    def add(
        display_name: str,
        dep_key: str,
        category: str,
        confidence: str = "high",
    ) -> None:
        key = dep_key.lower()
        in_deps = key in all_deps
        is_self = self_name == key
        if not (in_deps or is_self):
            return
        evidence = (
            find_evidence_dep(dep_key)
            if in_deps
            else (self_evidence or "found in dependencies")
        )
        detected.append(
            DetectedFramework(
                name=display_name,
                category=category,
                evidence=evidence,
                confidence=confidence,
            )
        )

    # Backend
    add("FastAPI", "fastapi", "backend")
    add("Django", "django", "backend")
    add("Flask", "flask", "backend")
    add("Express", "express", "backend")
    add("NestJS", "@nestjs/core", "backend")

    # Frontend
    add("Next.js", "next", "frontend")
    add("React", "react", "frontend")
    add("Vue", "vue", "frontend")
    add("Svelte", "svelte", "frontend")

    # ORM
    add("SQLAlchemy", "sqlalchemy", "orm")
    add("Prisma", "prisma", "orm")
    add("Prisma", "@prisma/client", "orm")
    add("Django ORM", "django", "orm", confidence="medium")

    # Testing
    if "pytest" in all_deps:
        detected.append(
            DetectedFramework(
                name="pytest",
                category="testing",
                evidence=find_evidence_dep("pytest"),
                confidence="high",
            )
        )
    elif any("conftest.py" in entry.get("path", "").lower() for entry in input.tree_entries):
        detected.append(
            DetectedFramework(
                name="pytest",
                category="testing",
                evidence="found conftest.py in tree",
                confidence="medium",
            )
        )
    add("Jest", "jest", "testing")
    add("Vitest", "vitest", "testing")

    # Deduplicate by (name, category) — keep first occurrence.
    seen: dict[tuple[str, str], DetectedFramework] = {}
    for fw in detected:
        key = (fw.name, fw.category)
        if key not in seen:
            seen[key] = fw

    return FrameworksInfo(detected=list(seen.values()))