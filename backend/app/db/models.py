from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# JSONB on PostgreSQL, plain JSON elsewhere so SQLite (tests) also works.
JSONVariant = JSON().with_variant(JSONB, "postgresql")


class RepositoryAnalysis(Base):
    __tablename__ = "repository_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(512), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_data: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    ai_summary: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    ai_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unavailable")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_repository_analysis_lookup", "repo_full_name", "commit_sha"),
    )
