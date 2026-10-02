import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_provider
from app.ai.prompts import build_explanation_prompt
from app.ai.schemas import AIResult
from app.analysis.engine import run_analysis
from app.analysis.inputs import AnalysisInput
from app.analysis.schemas import AnalysisResult
from app.core.config import settings
from app.db.repositories.repository_analysis import get_cached, save_analysis
from app.integrations.github.client import GitHubClient
from app.integrations.github.constants import MAX_FILES_TO_AI, MAX_TOTAL_CONTENT_BYTES
from app.integrations.github.exceptions import GitHubError
from app.integrations.github.selectors import select_priority_files
from app.integrations.github.urls import parse_github_url
from app.schemas.orchestrator import AnalysisResponse

logger = logging.getLogger(__name__)





async def orchestrate_analysis(
    repo_url: str,
    github_client: GitHubClient | None = None,
    session: AsyncSession | None = None,
) -> AnalysisResponse:
    owner, repo = parse_github_url(repo_url)

    client = github_client or GitHubClient(token=settings.GITHUB_TOKEN)
    should_close_client = github_client is None

    try:
        metadata = await client.get_repository(owner, repo)
        tree_resp = await client.get_tree(owner, repo, metadata.default_branch)

        if session is not None:
            cached = await get_cached(session, metadata.full_name, tree_resp.sha)
            if cached is not None:
                return _response_from_cache(repo_url, metadata.full_name, tree_resp.sha, cached)

        entries = tree_resp.entries
        priority_files = select_priority_files(entries, max_count=MAX_FILES_TO_AI)

        file_contents: dict[str, str] = {}
        total_size = 0

        for entry in priority_files:
            if total_size >= MAX_TOTAL_CONTENT_BYTES:
                break
            try:
                content_obj = await client.get_file_content(
                    owner, repo, entry.path, metadata.default_branch
                )
                content_bytes = content_obj.content.encode("utf-8")
                content_size = len(content_bytes)

                if total_size + content_size > MAX_TOTAL_CONTENT_BYTES:
                    break

                file_contents[entry.path] = content_obj.content
                total_size += content_size
            except GitHubError:
                raise
            except Exception as exc:
                logger.warning("Failed to fetch content for %s: %s", entry.path, exc)
                continue
    finally:
        if should_close_client:
            await client.close()

    analysis_input = AnalysisInput.from_dicts(
        metadata.model_dump(),
        [entry.model_dump() for entry in entries],
        file_contents,
    )
    analysis_result = run_analysis(analysis_input)

    prompt = build_explanation_prompt(analysis_result)

    provider = get_provider()
    try:
        ai_result = await provider.generate_explanation(analysis_result, prompt)
    except Exception as exc:
        logger.error("AI provider error: %s", exc)
        ai_result = AIResult(
            status="error",
            provider=getattr(provider, "name", "unknown"),
            model=getattr(provider, "model", None),
            explanation=None,
            error_message=str(exc),
            generated_at=datetime.now(timezone.utc),
        )
    finally:
        if hasattr(provider, "close"):
            await provider.close()

    if session is not None:
        await save_analysis(
            session,
            repo_full_name=metadata.full_name,
            repo_url=repo_url,
            commit_sha=tree_resp.sha,
            default_branch=metadata.default_branch,
            analysis_data=analysis_result.model_dump(mode="json"),
            ai_summary=ai_result.model_dump(mode="json"),
            ai_status=ai_result.status,
        )

    return AnalysisResponse(
        repo_url=repo_url,
        repo_full_name=metadata.full_name,
        commit_sha=tree_resp.sha,
        from_cache=False,
        analyzed_at=datetime.now(timezone.utc),
        analysis=analysis_result,
        ai=ai_result,
    )


def _response_from_cache(
    repo_url: str, repo_full_name: str, commit_sha: str, cached
) -> AnalysisResponse:
    analysis = AnalysisResult.model_validate(cached.analysis_data)
    if cached.ai_summary:
        ai = AIResult.model_validate(cached.ai_summary)
    else:
        ai = AIResult(
            status=cached.ai_status or "unavailable",
            provider="cache",
            error_message="Cached entry has no AI summary",
            generated_at=cached.created_at,
        )
    return AnalysisResponse(
        repo_url=repo_url,
        repo_full_name=repo_full_name,
        commit_sha=commit_sha,
        from_cache=True,
        analyzed_at=datetime.now(timezone.utc),
        analysis=analysis,
        ai=ai,
    )
