from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RepositoryInfo(BaseModel):
    full_name: str
    owner: str
    name: str
    description: str | None
    default_branch: str
    stars: int
    forks: int
    license: str | None
    html_url: str

class LanguagesInfo(BaseModel):
    primary: str | None
    detected: dict[str, int]
    source: str | None

class StructureInfo(BaseModel):
    total_files: int
    total_directories: int
    top_level_entries: list[str]
    depth_estimate: int
    max_depth_path: str | None
    has_backend_folder: bool
    has_frontend_folder: bool
    has_docs_folder: bool
    has_tests_folder: bool
    common_config_files: list[str]

class DocumentationInfo(BaseModel):
    has_readme: bool
    readme_path: str | None
    readme_size_bytes: int | None
    has_license: bool
    license_path: str | None
    has_contributing: bool
    has_changelog: bool
    has_docs_folder: bool
    docs_files_count: int

class DetectedFramework(BaseModel):
    name: str
    category: str
    evidence: str
    confidence: str

class DependenciesInfo(BaseModel):
    has_manifest: bool
    manifest_files: list[str]
    ecosystems: list[str]
    runtime_dependencies: dict[str, str]
    dev_dependencies: dict[str, str]
    total_count: int

class FrameworksInfo(BaseModel):
    detected: list[DetectedFramework]

class AnalysisResult(BaseModel):
    analyzer_version: str
    analyzed_at: datetime
    repository: RepositoryInfo
    languages: LanguagesInfo
    structure: StructureInfo
    documentation: DocumentationInfo
    dependencies: DependenciesInfo
    frameworks: FrameworksInfo
