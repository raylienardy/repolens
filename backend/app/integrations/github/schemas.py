from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    full_name: str
    owner: str
    description: str | None = None
    default_branch: str
    size: int
    stars: int
    forks: int
    open_issues: int
    language: str | None = None
    languages_url: str
    license: str | None = None
    is_private: bool
    html_url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime

class TreeEntry(BaseModel):
    path: str
    type: Literal["blob", "tree"]
    size: int | None = None
    sha: str

class TreeResponse(BaseModel):
    entries: list[TreeEntry]
    truncated: bool
    sha: str

class FileContent(BaseModel):
    path: str
    content: str
    size: int
    encoding: str
