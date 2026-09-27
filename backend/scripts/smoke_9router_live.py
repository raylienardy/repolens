import asyncio, json, os
from app.ai.factory import get_provider
from app.analysis.schemas import (
    AnalysisResult, RepositoryInfo, LanguagesInfo,
    StructureInfo, DocumentationInfo, DependenciesInfo, FrameworksInfo,
    TestingInfo, ConfigurationInfo, SecuritySignalsInfo, EntryPointInfo
)
from app.ai.prompts import build_explanation_prompt

async def main():
    # Bangun AnalysisResult minimal
    result = AnalysisResult(
        analyzer_version="0.1.0",
        analyzed_at="2026-09-27T00:00:00Z",
        repository=RepositoryInfo(full_name="test/demo", owner="test", name="demo",
            description="Demo", default_branch="main", stars=1, forks=0,
            license="MIT", html_url="https://github.com/test/demo"),
        languages=LanguagesInfo(primary="Python", detected={".py": 5}, source="both"),
        structure=StructureInfo(total_files=5, total_directories=2,
            top_level_entries=["app", "README.md"], depth_estimate=2,
            max_depth_path="app/main.py", has_backend_folder=True,
            has_frontend_folder=False, has_docs_folder=False,
            has_tests_folder=False, common_config_files=["pyproject.toml"]),
        documentation=DocumentationInfo(has_readme=True, readme_path="README.md",
            readme_size_bytes=100, has_license=True, license_path="LICENSE",
            has_contributing=False, has_changelog=False, has_docs_folder=False,
            docs_files_count=0),
        dependencies=DependenciesInfo(has_manifest=True, manifest_files=["pyproject.toml"],
            ecosystems=["python"], runtime_dependencies={"fastapi": ">=0.100"},
            dev_dependencies={}, total_count=1),
        frameworks=FrameworksInfo(detected=[]),
        testing=TestingInfo(has_tests_folder=False, tests_folder_path=None,
            test_files_count=0, test_files=[], has_test_config=False,
            test_config_files=[], has_ci_test_workflow=False),
        configuration=ConfigurationInfo(config_files=[], has_docker=False,
            has_docker_compose=False, has_ci=False, has_env_example=False,
            has_makefile=False),
        security_signals=SecuritySignalsInfo(has_security_md=False,
            has_dependabot=False, has_env_example=False, has_gitignore=False,
            has_license=True, signals_found=1, signals_total=5),
        entry_points=EntryPointInfo(found=[]),
    )
    prompt = build_explanation_prompt(result)
    provider = get_provider()
    print(f"PROVIDER: {provider.name}")
    ai_result = await provider.generate_explanation(result, prompt)
    print(f"STATUS: {ai_result.status}")
    print(f"MODEL: {ai_result.model}")
    if ai_result.explanation:
        print(f"SUMMARY (first 200 chars): {ai_result.explanation.summary[:200]}")
    if ai_result.error_message:
        print(f"ERROR: {ai_result.error_message}")
    if hasattr(provider, "close"):
        await provider.close()

asyncio.run(main())
