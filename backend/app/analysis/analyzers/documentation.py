from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import DocumentationInfo

def analyze_documentation(input: AnalysisInput) -> DocumentationInfo:
    root_files = [PurePosixPath(e.get("path", "")).name.lower() for e in input.tree_entries if "/" not in e.get("path", "")]
    
    readme = next((e for e in input.tree_entries if PurePosixPath(e.get("path", "")).name.lower() in ["readme.md", "readme.rst", "readme.txt"] and "/" not in e.get("path", "")), None)
    license = next((e for e in input.tree_entries if "license" in PurePosixPath(e.get("path", "")).name.lower() and "/" not in e.get("path", "")), None)
    
    return DocumentationInfo(
        has_readme=bool(readme),
        readme_path=readme.get("path") if readme else None,
        readme_size_bytes=readme.get("size") if readme else None,
        has_license=bool(license),
        license_path=license.get("path") if license else None,
        has_contributing=any(n in ["contributing.md", "contributing.rst"] for n in root_files),
        has_changelog=any(n in ["changelog.md", "changes.md", "history.md"] for n in root_files),
        has_docs_folder=any(PurePosixPath(e.get("path", "")).parts[0] in ["docs", "doc"] for e in input.tree_entries),
        docs_files_count=len([e for e in input.tree_entries if e.get("path", "").startswith("docs/")])
    )
