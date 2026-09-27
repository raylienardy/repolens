// Types matching backend schemas (snake_case)
export interface RepositoryInfo {
  full_name: string;
  owner: string;
  name: string;
  description: string | null;
  default_branch: string;
  stars: number;
  forks: number;
  license: string | null;
  html_url: string;
}

export interface LanguagesInfo {
  primary: string | null;
  detected: Record<string, number>;
  source: string | null;
}

export interface StructureInfo {
  total_files: number;
  total_directories: number;
  top_level_entries: string[];
  depth_estimate: number;
  max_depth_path: string | null;
  has_backend_folder: boolean;
  has_frontend_folder: boolean;
  has_docs_folder: boolean;
  has_tests_folder: boolean;
  common_config_files: string[];
}

export interface DocumentationInfo {
  has_readme: boolean;
  readme_path: string | null;
  readme_size_bytes: number | null;
  has_license: boolean;
  license_path: string | null;
  has_contributing: boolean;
  has_changelog: boolean;
  has_docs_folder: boolean;
  docs_files_count: number;
}

export interface DependenciesInfo {
  has_manifest: boolean;
  manifest_files: string[];
  ecosystems: string[];
  runtime_dependencies: Record<string, string>;
  dev_dependencies: Record<string, string>;
  total_count: number;
}

export interface DetectedFramework {
  name: string;
  category: string;
  evidence: string;
  confidence: string;
}

export interface FrameworksInfo {
  detected: DetectedFramework[];
}

export interface TestingInfo {
  has_tests_folder: boolean;
  tests_folder_path: string | null;
  test_files_count: number;
  test_files: string[];
  has_test_config: boolean;
  test_config_files: string[];
  has_ci_test_workflow: boolean;
}

export interface ConfigurationInfo {
  config_files: string[];
  has_docker: boolean;
  has_docker_compose: boolean;
  has_ci: boolean;
  has_env_example: boolean;
  has_makefile: boolean;
}

export interface SecuritySignalsInfo {
  has_security_md: boolean;
  has_dependabot: boolean;
  has_env_example: boolean;
  has_gitignore: boolean;
  has_license: boolean;
  signals_found: number;
  signals_total: number;
}

export interface EntryPoint {
  path: string;
  kind: string;
  evidence: string;
}

export interface EntryPointInfo {
  found: EntryPoint[];
}

export interface AnalysisResult {
  analyzer_version: string;
  analyzed_at: string; // ISO datetime
  repository: RepositoryInfo;
  languages: LanguagesInfo;
  structure: StructureInfo;
  documentation: DocumentationInfo;
  dependencies: DependenciesInfo;
  frameworks: FrameworksInfo;
  testing: TestingInfo;
  configuration: ConfigurationInfo;
  security_signals: SecuritySignalsInfo;
  entry_points: EntryPointInfo;
}

export interface AIExplanation {
  summary: string;
  purpose: string;
  key_technologies: string[];
  architecture_notes: string;
  notable_findings: string[];
  improvement_suggestions: string[];
  inference_disclaimer: string;
}

export interface AIResult {
  status: string;
  provider: string;
  model: string | null;
  explanation: AIExplanation | null;
  error_message: string | null;
  generated_at: string;
  prompt_tokens: number | null;
  completion_tokens: number | null;
}

export interface AnalysisResponse {
  repo_url: string;
  repo_full_name: string;
  commit_sha: string;
  from_cache: boolean;
  analyzed_at: string;
  analysis: AnalysisResult;
  ai: AIResult;
}

export interface AnalyzeRequest {
  repo_url: string;
}

export interface ApiError {
  detail: string;
}
