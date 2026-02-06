"""Pydantic models for Racing API meets endpoint."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Meet(BaseModel):
    """Single race meet/meeting."""

    country: str = Field(..., description="Country code (e.g., 'USA')")
    date: str = Field(..., description="Meet date in YYYY-MM-DD format")
    meet_id: str = Field(..., description="Unique meet identifier")
    track_id: str = Field(..., description="Track code (e.g., 'BEL', 'CD')")
    track_name: str = Field(..., description="Full track name")

    class Config:
        json_schema_extra = {
            "example": {
                "country": "USA",
                "date": "2024-02-05",
                "meet_id": "202402051234",
                "track_id": "BEL",
                "track_name": "Belmont Park"
            }
        }


class MeetsResponse(BaseModel):
    """Response from /meets endpoint."""

    meets: List[Meet] = Field(default_factory=list, description="List of meets")
    limit: int = Field(..., description="Results limit")
    skip: int = Field(..., description="Results offset")
    query: Optional[List] = Field(None, description="Query metadata")

    @property
    def total_meets(self) -> int:
        """Total number of meets returned."""
        return len(self.meets)

    def get_tracks(self) -> List[str]:
        """Get unique list of track names."""
        return list(set(meet.track_name for meet in self.meets))

    def filter_by_track(self, track_name: str) -> List[Meet]:
        """Filter meets by track name."""
        return [meet for meet in self.meets if meet.track_name == track_name]