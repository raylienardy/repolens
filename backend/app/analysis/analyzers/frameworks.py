from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import DependenciesInfo, DetectedFramework, FrameworksInfo

def analyze_frameworks(input: AnalysisInput, deps: DependenciesInfo) -> FrameworksInfo:
    detected: list[DetectedFramework] = []
    
    # Helper to find which file provided a dependency
    def find_evidence_dep(dep_name: str) -> str:
        dep_lower = dep_name.lower()
        for path, content in input.file_contents.items():
            if dep_lower in content.lower():
                return f"found in {PurePosixPath(path).name}"
        return "found in dependencies"

    # Combine all dependencies for lookup
    all_deps = {**deps.runtime_dependencies, **deps.dev_dependencies}

    # Rules definitions
    # Backend
    if "fastapi" in all_deps:
        detected.append(DetectedFramework(
            name="FastAPI", category="backend", evidence=find_evidence_dep("fastapi"), confidence="high"
        ))
    if "django" in all_deps:
        detected.append(DetectedFramework(
            name="Django", category="backend", evidence=find_evidence_dep("django"), confidence="high"
        ))
    if "flask" in all_deps:
        detected.append(DetectedFramework(
            name="Flask", category="backend", evidence=find_evidence_dep("flask"), confidence="high"
        ))
    if "express" in all_deps:
        detected.append(DetectedFramework(
            name="Express", category="backend", evidence=find_evidence_dep("express"), confidence="high"
        ))
    if "@nestjs/core" in all_deps:
        detected.append(DetectedFramework(
            name="NestJS", category="backend", evidence=find_evidence_dep("@nestjs/core"), confidence="high"
        ))

    # Frontend
    if "next" in all_deps:
        detected.append(DetectedFramework(
            name="Next.js", category="frontend", evidence=find_evidence_dep("next"), confidence="high"
        ))
    if "react" in all_deps:
        detected.append(DetectedFramework(
            name="React", category="frontend", evidence=find_evidence_dep("react"), confidence="high"
        ))
    if "vue" in all_deps:
        detected.append(DetectedFramework(
            name="Vue", category="frontend", evidence=find_evidence_dep("vue"), confidence="high"
        ))
    if "svelte" in all_deps:
        detected.append(DetectedFramework(
            name="Svelte", category="frontend", evidence=find_evidence_dep("svelte"), confidence="high"
        ))

    # ORM
    if "sqlalchemy" in all_deps:
        detected.append(DetectedFramework(
            name="SQLAlchemy", category="orm", evidence=find_evidence_dep("sqlalchemy"), confidence="high"
        ))
    if "prisma" in all_deps or "@prisma/client" in all_deps:
        ev = find_evidence_dep("prisma") if "prisma" in all_deps else find_evidence_dep("@prisma/client")
        detected.append(DetectedFramework(
            name="Prisma", category="orm", evidence=ev, confidence="high"
        ))
    if "django" in all_deps:
        detected.append(DetectedFramework(
            name="Django ORM", category="orm", evidence=find_evidence_dep("django"), confidence="medium"
        ))

    # Testing
    if "pytest" in all_deps:
        detected.append(DetectedFramework(
            name="pytest", category="testing", evidence=find_evidence_dep("pytest"), confidence="high"
        ))
    elif any("conftest.py" in entry.get("path", "").lower() for entry in input.tree_entries):
        detected.append(DetectedFramework(
            name="pytest", category="testing", evidence="found conftest.py in tree", confidence="medium"
        ))

    if "jest" in all_deps:
        detected.append(DetectedFramework(
            name="Jest", category="testing", evidence=find_evidence_dep("jest"), confidence="high"
        ))
    if "vitest" in all_deps:
        detected.append(DetectedFramework(
            name="Vitest", category="testing", evidence=find_evidence_dep("vitest"), confidence="high"
        ))

    return FrameworksInfo(detected=detected)
