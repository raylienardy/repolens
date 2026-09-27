import asyncio
import json
import sys

import httpx

sys.path.insert(0, ".")

from app.ai import AIProvider, build_explanation_prompt, get_provider
from app.ai.providers.mock import MockProvider
from app.ai.providers.ninerouter import NineRouterProvider
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


EXPLANATION_PAYLOAD = {
    "summary": "Repo penjelasan ringkas dari skenario A.",
    "purpose": "Menjelaskan validasi MockTransport.",
    "key_technologies": ["Python", "FastAPI"],
    "architecture_notes": "Struktur mock untuk pengujian.",
    "notable_findings": ["fakta 1", "fakta 2"],
    "improvement_suggestions": ["tambahkan SECURITY.md"],
    "inference_disclaimer": "Hasil mock; bukan AI nyata.",
}

FAKE_KEY = "test-key-not-real"


def _ok_transport():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": json.dumps(EXPLANATION_PAYLOAD)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            },
        )

    return httpx.MockTransport(handler)


async def run_mock_smoke(analysis, prompt: str) -> None:
    """Phase 7a regression: MockProvider behavior must stay intact."""
    print("=" * 60)
    print("REGRESI MOCK (Phase 7a)")
    print("=" * 60)

    provider = get_provider()
    print("PROVIDER:", provider.name, "| type:", type(provider).__name__)
    assert isinstance(provider, MockProvider), "expected MockProvider"
    assert isinstance(provider, AIProvider)

    result = await provider.generate_explanation(analysis, prompt)
    assert result.status == "ok"
    assert result.explanation is not None and result.explanation.summary.strip()
    assert result.provider == "mock" and result.model == "mock-v1"

    again = await provider.generate_explanation(analysis, prompt)
    assert again.explanation == result.explanation

    print("VERIFIED: mock status=ok, explanation present, deterministic")


async def run_transport_scenarios(analysis, prompt: str) -> None:
    assert isinstance(NineRouterProvider(api_key=FAKE_KEY), AIProvider)

    print("\n" + "=" * 60)
    print("SKENARIO A: MockTransport -> respons valid")
    print("=" * 60)
    provider = NineRouterProvider(api_key=FAKE_KEY, transport=_ok_transport())
    result = await provider.generate_explanation(analysis, prompt)
    await provider.close()
    assert result.status == "ok", result.model_dump_json()
    assert result.explanation is not None
    assert result.explanation.summary == EXPLANATION_PAYLOAD["summary"]
    assert result.prompt_tokens == 10 and result.completion_tokens == 20
    print("VERIFIED: status=ok, explanation terisi, usage=(10, 20)")

    print("\n" + "=" * 60)
    print("SKENARIO B: MockTransport -> HTTP 500")
    print("=" * 60)

    async def fail_500(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="upstream exploded (no secret here)")

    provider = NineRouterProvider(
        api_key=FAKE_KEY, transport=httpx.MockTransport(fail_500)
    )
    result = await provider.generate_explanation(analysis, prompt)
    await provider.close()
    assert result.status == "error" and result.explanation is None
    assert result.error_message and FAKE_KEY not in result.error_message
    print("VERIFIED: status=error ->", result.error_message)

    print("\n" + "=" * 60)
    print("SKENARIO C: MockTransport -> body bukan JSON")
    print("=" * 60)

    async def not_json(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="ini bukan json")

    provider = NineRouterProvider(
        api_key=FAKE_KEY, transport=httpx.MockTransport(not_json)
    )
    result = await provider.generate_explanation(analysis, prompt)
    await provider.close()
    assert result.status == "error" and result.explanation is None
    assert FAKE_KEY not in (result.error_message or "")
    print("VERIFIED: status=error ->", result.error_message)

    print("\n" + "=" * 60)
    print("SKENARIO D: MockTransport -> JSON tanpa skema AIExplanation")
    print("=" * 60)

    async def bad_schema(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"summary": "hanya satu field"}'}}]},
        )

    provider = NineRouterProvider(
        api_key=FAKE_KEY, transport=httpx.MockTransport(bad_schema)
    )
    result = await provider.generate_explanation(analysis, prompt)
    await provider.close()
    assert result.status == "error" and result.explanation is None
    print("VERIFIED: status=error ->", result.error_message)


async def run_factory_validation() -> None:
    from app.core import config as config_module

    original_provider = config_module.settings.AI_PROVIDER
    original_key = config_module.settings.AI_API_KEY
    try:
        config_module.settings.AI_PROVIDER = "mock"
        assert isinstance(get_provider(), MockProvider)
        print("\nVERIFIED: factory returns MockProvider for 'mock'")

        config_module.settings.AI_PROVIDER = "9router"
        config_module.settings.AI_API_KEY = None
        try:
            get_provider()
            raise AssertionError("expected ValueError for missing AI_API_KEY")
        except ValueError as exc:
            print("VERIFIED: factory rejects 9router without AI_API_KEY ->", exc)

        config_module.settings.AI_API_KEY = "dummy-for-validation"
        assert isinstance(get_provider(), NineRouterProvider)
        print("VERIFIED: factory returns NineRouterProvider when AI_API_KEY set")

        config_module.settings.AI_PROVIDER = "unknown-xyz"
        try:
            get_provider()
            raise AssertionError("expected ValueError for unknown provider")
        except ValueError as exc:
            print("VERIFIED: factory rejects unknown provider ->", exc)
    finally:
        config_module.settings.AI_PROVIDER = original_provider
        config_module.settings.AI_API_KEY = original_key


async def main() -> None:
    analysis = build_sample_analysis()
    prompt = build_explanation_prompt(analysis)
    print("PROMPT (length=%d chars, ~%d tokens)" % (len(prompt), len(prompt) // 4))

    await run_mock_smoke(analysis, prompt)
    await run_transport_scenarios(analysis, prompt)
    await run_factory_validation()
    print("\nALL SCENARIOS PASSED; no real 9router connection was used.")


if __name__ == "__main__":
    asyncio.run(main())
