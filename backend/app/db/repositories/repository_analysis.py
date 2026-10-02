from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RepositoryAnalysis

DEFAULT_TTL_DAYS = 7


async def get_cached(
    session: AsyncSession,
    repo_full_name: str,
    commit_sha: str,
) -> RepositoryAnalysis | None:
    now = datetime.now(timezone.utc)
    stmt = (
        select(RepositoryAnalysis)
        .where(
            RepositoryAnalysis.repo_full_name == repo_full_name,
            RepositoryAnalysis.commit_sha == commit_sha,
        )
        .order_by(RepositoryAnalysis.id.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return None
    if row.expires_at is not None:
        expires_at = row.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            return None
    return row


async def save_analysis(
    session: AsyncSession,
    repo_full_name: str,
    repo_url: str,
    commit_sha: str,
    default_branch: str,
    analysis_data: dict,
    ai_summary: dict | None,
    ai_status: str,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> RepositoryAnalysis:
    record = RepositoryAnalysis(
        repo_full_name=repo_full_name,
        repo_url=repo_url,
        commit_sha=commit_sha,
        default_branch=default_branch,
        analysis_data=analysis_data,
        ai_summary=ai_summary,
        ai_status=ai_status,
        expires_at=datetime.now(timezone.utc) + timedelta(days=ttl_days),
    )
    session.add(record)
    try:
        await session.commit()
        await session.refresh(record)
        return record
    except IntegrityError:
        # Race condition: another request inserted the same (repo, commit) first.
        # Roll back and return the existing record instead of failing.
        await session.rollback()
        existing = await get_cached(session, repo_full_name, commit_sha)
        if existing is None:
            raise
        return existing