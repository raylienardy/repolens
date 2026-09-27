from pydantic import BaseModel, Field

class AnalysisInput(BaseModel):
    repository_metadata: dict
    tree_entries: list[dict]
    file_contents: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_dicts(cls, metadata: dict, tree_entries: list[dict], file_contents: dict[str, str] | None = None):
        return cls(
            repository_metadata=metadata,
            tree_entries=tree_entries,
            file_contents=file_contents or {}
        )
