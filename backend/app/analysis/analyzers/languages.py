from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import LanguagesInfo

def analyze_languages(input: AnalysisInput) -> LanguagesInfo:
    meta = input.repository_metadata
    primary = meta.get("language")
    
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
        ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C",
        ".md": "Markdown", ".yml": "YAML", ".yaml": "YAML", ".json": "JSON"
    }
    
    detected = {}
    for entry in input.tree_entries:
        if entry.get("type") == "blob":
            path = entry.get("path", "")
            ext = PurePosixPath(path).suffix.lower()
            detected[ext] = detected.get(ext, 0) + 1
            
    source = None
    if primary and detected: source = "both"
    elif primary: source = "metadata"
    elif detected: source = "tree"
        
    return LanguagesInfo(primary=primary, detected=detected, source=source)
