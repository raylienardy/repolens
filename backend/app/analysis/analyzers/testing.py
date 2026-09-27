import re
from pathlib import PurePosixPath
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import TestingInfo

def analyze_testing(input: AnalysisInput) -> TestingInfo:
    test_files: list[str] = []
    tests_folder_path: str | None = None
    test_config_files: list[str] = []
    has_ci_test_workflow: bool = False

    known_test_configs = {
        "pytest.ini", "tox.ini", "jest.config.js", "jest.config.ts",
        "vitest.config.ts", "vitest.config.js"
    }

    test_pattern = re.compile(
        r"^(test_.*\.py|.*_test\.py|.*\.test\.ts|.*\.test\.js|.*\.spec\.ts|.*\.spec\.js|.*_test\.go|conftest\.py|.*_test\.rs)$",
        re.IGNORECASE
    )

    for entry in input.tree_entries:
        path = entry.get("path", "")
        norm_path = path.lower()
        parts = PurePosixPath(norm_path).parts
        filename = PurePosixPath(norm_path).name

        # Detect tests folder
        if parts:
            if parts[0] in {"tests", "test", "__tests__"}:
                if tests_folder_path is None:
                    tests_folder_path = entry.get("path", "").split("/")[0]

        # Detect CI test workflow
        if norm_path.startswith(".github/workflows/") and entry.get("type") == "blob":
            if "test" in filename or "ci" in filename:
                has_ci_test_workflow = True

        # Detect test configs
        if filename in known_test_configs:
            test_config_files.append(entry.get("path", ""))

        # Detect test files
        if entry.get("type") == "blob":
            in_test_dir = any(p in {"tests", "test", "__tests__"} for p in parts[:-1])
            matches_pattern = bool(test_pattern.match(filename))
            if in_test_dir or matches_pattern:
                test_files.append(entry.get("path", ""))

    has_tests_folder = tests_folder_path is not None
    test_files_count = len(test_files)

    return TestingInfo(
        has_tests_folder=has_tests_folder,
        tests_folder_path=tests_folder_path,
        test_files_count=test_files_count,
        test_files=test_files[:10],
        has_test_config=len(test_config_files) > 0,
        test_config_files=test_config_files,
        has_ci_test_workflow=has_ci_test_workflow,
    )
