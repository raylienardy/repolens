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

class TestingInfo(BaseModel):
    has_tests_folder: bool
    tests_folder_path: str | None
    test_files_count: int
    test_files: list[str]
    has_test_config: bool
    test_config_files: list[str]
    has_ci_test_workflow: bool

class ConfigurationInfo(BaseModel):
    config_files: list[str]
    has_docker: bool
    has_docker_compose: bool
    has_ci: bool
    has_env_example: bool
    has_makefile: bool

class SecuritySignalsInfo(BaseModel):
    # SIGNALS, bukan verdict. Hanya melaporkan keberadaan file indikatif.
    has_security_md: bool
    has_dependabot: bool
    has_env_example: bool
    has_gitignore: bool
    has_license: bool
    signals_found: int
    signals_total: int = 5

class EntryPoint(BaseModel):
    path: str
    kind: str
    evidence: str

class EntryPointInfo(BaseModel):
    found: list[EntryPoint]

class AnalysisResult(BaseModel):
    analyzer_version: str
    analyzed_at: datetime
    repository: RepositoryInfo
    languages: LanguagesInfo
    structure: StructureInfo
    documentation: DocumentationInfo
    dependencies: DependenciesInfo
    frameworks: FrameworksInfo
    testing: TestingInfo
    configuration: ConfigurationInfo
    security_signals: SecuritySignalsInfo
    entry_points: EntryPointInfo
