from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.integrations.github.exceptions import (
    GitHubError,
    InvalidGitHubUrlError,
    RateLimitError,
    RepositoryNotFoundError,
    RepositoryPrivateError,
    RepositoryTooLargeError,
)
from app.schemas.api import AnalyzeRequest
from app.schemas.orchestrator import AnalysisResponse
from app.services.orchestrator import orchestrate_analysis

router = APIRouter()


@router.post("", response_model=AnalysisResponse)
async def analyze_repo(
    payload: AnalyzeRequest, session: AsyncSession = Depends(get_db)
) -> AnalysisResponse:
    try:
        return await orchestrate_analysis(payload.repo_url, session=session)
    except InvalidGitHubUrlError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="URL GitHub tidak valid"
        )
    except RepositoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found"
        )
    except RepositoryPrivateError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Repository is private"
        )
    except RepositoryTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Repository too large"
        )
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="GitHub rate limit exceeded"
        )
    except GitHubError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="GitHub API error"
        )
