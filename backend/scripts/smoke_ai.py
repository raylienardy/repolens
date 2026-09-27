import asyncio
import json
import sys

sys.path.insert(0, ".")

from app.ai import AIProvider, build_explanation_prompt, get_provider
from app.ai.providers.mock import MockProvider
from app.analysis.engine import run_analysis
from app.analysis.inputs import AnalysisInput


def build_sample_analysis():
    meta = {
        "full_name": "acme/api-service", "owner": "acme", "name": "api-service",
        "description": "REST API service for internal tooling",
        "default_branch": "main", "stars": 42, "forks": 7,
        "license": "MIT", "html_url": "https://github.com/acme/api-service",
        "language": "Python",
    }
    tree = [
        {"path": "README.md", "type": "blob", "size": 1200},
        {"path": "LICENSE", "type": "blob", "size": 1100},
        {"path": ".gitignore", "type": "blob", "size": 100},
        {"path": "pyproject.toml", "type": "blob", "size": 400},
        {"path": "Dockerfile", "type": "blob", "size": 200},
        {"path": "app", "type": "tree"},
        {"path": "app/main.py", "type": "blob", "size": 900},
        {"path": "app/api/routes.py", "type": "blob", "size": 1400},
        {"path": "tests", "type": "tree"},
        {"path": "tests/test_main.py", "type": "blob", "size": 300},
        {"path": "pytest.ini", "type": "blob", "size": 80},
    ]
    pyproject = """
[project]
name = "api-service"
version = "0.1.0"
dependencies = ["fastapi>=0.100", "sqlalchemy>=2.0", "httpx>=0.27"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
"""
    return run_analysis(
        AnalysisInput.from_dicts(meta, tree, {"pyproject.toml": pyproject})
    )


async def main() -> None:
    analysis = build_sample_analysis()

    prompt = build_explanation_prompt(analysis)
    print("=" * 60)
    print("PROMPT (length=%d chars, ~%d tokens)" % (len(prompt), len(prompt) // 4))
    print("=" * 60)
    print(prompt)
    print()

    provider = get_provider()
    print("PROVIDER:", provider.name, "| type:", type(provider).__name__)
    assert isinstance(provider, MockProvider), "expected MockProvider"
    assert isinstance(provider, AIProvider), "MockProvider should satisfy AIProvider protocol"

    result = await provider.generate_explanation(analysis, prompt)

    print("=" * 60)
    print("AI RESULT")
    print("=" * 60)
    print(json.dumps(json.loads(result.model_dump_json()), indent=2, ensure_ascii=False))

    assert result.status == "ok", f"expected status ok, got {result.status}"
    assert result.explanation is not None, "explanation must not be None"
    assert result.explanation.summary.strip(), "summary must not be empty"
    assert result.provider == "mock"
    assert result.model == "mock-v1"
    assert result.prompt_tokens is None and result.completion_tokens is None

    # Determinism check: same input must yield same explanation
    again = await provider.generate_explanation(analysis, prompt)
    assert again.explanation == result.explanation, "mock provider must be deterministic"
    print("\nVERIFIED: status=ok, explanation present, summary non-empty, output deterministic")

    # Factory error path
    from app.core import config as config_module
    original = config_module.settings.AI_PROVIDER
    config_module.settings.AI_PROVIDER = "9router"
    try:
        get_provider()
        print("ERROR: expected ValueError for unknown provider")
    except ValueError as exc:
        print("VERIFIED: factory raises ValueError for unknown provider ->", exc)
    finally:
        config_module.settings.AI_PROVIDER = original


if __name__ == "__main__":
    asyncio.run(main())
