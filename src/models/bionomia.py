"""
Bionomia API models for name normalization and matching.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TypedDict


class BionomiaNameRecord(BaseModel):
    """A Bionomia name record from the API response"""

    model_config = ConfigDict(
        extra="allow"
    )  # Allow extra fields like match_reason, match_id

    id: Optional[int] = Field(None, description="Bionomia user ID")
    score: Optional[float] = Field(None, description="API similarity score")
    orcid: Optional[str] = Field(None, description="ORCID identifier")
    wikidata: Optional[str] = Field(
        None, description="Wikidata identifier (e.g., 'Q113489547')"
    )
    uri: Optional[str] = Field(None, description="URI to the person's record")
    fullname: Optional[str] = Field(None, description="Full name of the person")
    fullname_reverse: Optional[str] = Field(
        None, description="Full name in reverse format (Last, First)"
    )
    given: Optional[str] = Field(None, description="Given name")
    family: Optional[str] = Field(None, description="Family name")
    label: Optional[str] = Field(None, description="Preferred label/display name")
    other_names: list[str] = Field(
        default_factory=list, description="List of alternative names"
    )
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    lifespan: Optional[str] = Field(None, description="Lifespan dates if known")
    description: Optional[str] = Field(None, description="Description of the person")
    is_public: Optional[bool] = Field(None, description="Whether the record is public")
    has_occurrences: Optional[bool] = Field(
        None, description="Whether the person has occurrence records"
    )


class NameMatchResult(TypedDict, total=False):
    """Result structure from find_best_name_match"""
    monologue: str
    matches: list[dict]  # List of BionomiaNameRecord dicts with match_reason and match_confidence


class BionomiaErrorResult(TypedDict):
    """Error result structure from normalize_name"""
    status: str
    original: str
    found_count: Optional[int]
    threshold: Optional[float]
    error: Optional[str]
    fallback: Optional[dict]

