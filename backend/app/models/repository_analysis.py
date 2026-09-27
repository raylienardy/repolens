import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class RepositoryAnalysis(Base):
    __tablename__ = "repository_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repo_full_name: Mapped[str] = mapped_column(
        String, index=True, nullable=False
    )
    repo_url: Mapped[str] = mapped_column(String, nullable=False)
    commit_sha: Mapped[str] = mapped_column(String, nullable=False)
    default_branch: Mapped[str | None] = mapped_column(String, nullable=True)
    analysis_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ai_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("repo_full_name", "commit_sha", name="uq_repo_commit"),
    )
