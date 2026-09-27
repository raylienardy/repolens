from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import StructureInfo

def analyze_structure(input: AnalysisInput) -> StructureInfo:
    files = [e for e in input.tree_entries if e.get("type") == "blob"]
    dirs = [e for e in input.tree_entries if e.get("type") == "tree"]
    
    top_level = []
    max_depth = 0
    max_path = None
    
    for entry in input.tree_entries:
        path = entry.get("path", "")
        parts = PurePosixPath(path).parts
        if len(parts) == 1:
            top_level.append(parts[0])
        if len(parts) > max_depth:
            max_depth = len(parts)
            max_path = path
            
    common_files = {"package.json", "pyproject.toml", "requirements.txt", "Dockerfile", 
                    "docker-compose.yml", ".env.example", "makefile", "tsconfig.json", 
                    "next.config.js", "next.config.ts", "vite.config.ts", "go.mod", "cargo.toml"}
    found_common = [PurePosixPath(e.get("path", "")).name for e in files if PurePosixPath(e.get("path", "")).name in common_files]
    
    return StructureInfo(
        total_files=len(files),
        total_directories=len(dirs),
        top_level_entries=top_level,
        depth_estimate=max_depth,
        max_depth_path=max_path,
        has_backend_folder=any(p in ["backend", "server", "api"] for p in top_level),
        has_frontend_folder=any(p in ["frontend", "client", "web"] for p in top_level),
        has_docs_folder=any(p in ["docs", "doc", "documentation"] for p in top_level),
        has_tests_folder=any(p in ["tests", "test", "__tests__"] for p in top_level),
        common_config_files=list(set(found_common))
    )
