"""Pydantic models for races."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List, Any
from datetime import datetime

from src.models.runner import Runner
from src.models.pools import RacePool


class RaceKey(BaseModel):
    """Race key identifier."""
    race_number: str = Field(..., description="Race number")
    day_evening: Optional[str] = Field(None, description="Day (D) or Evening (E)")


class Change(BaseModel):
    """Race change notification."""
    type: Optional[str] = Field(None, description="Change type")
    text: Optional[str] = Field(None, description="Change description")


class Race(BaseModel):
    """Individual race with runners."""

    # Identifiers
    race_key: RaceKey = Field(..., description="Race key")
    race_name: Optional[str] = Field(None, description="Race name")

    # Timing
    post_time: Optional[str] = Field(None, description="Post time (e.g., '12:30 PM')")
    post_time_long: Optional[str] = Field(None, description="Post time in long format")
    mtp: Optional[int] = Field(None, description="Minutes to post")

    # Race Details
    distance_value: Optional[int] = Field(None, description="Distance value")
    distance_unit: Optional[str] = Field(None, description="Distance unit (Furlongs, etc.)")
    distance_description: Optional[str] = Field(None, description="Distance description")
    surface_description: Optional[str] = Field(None, description="Surface (Dirt, Turf, etc.)")
    track_condition: Optional[str] = Field(None, description="Track condition (Fast, Muddy, etc.)")

    # Classification
    race_type: Optional[str] = Field(None, description="Race type code")
    race_type_description: Optional[str] = Field(None, description="Race type description")
    race_class: Optional[str] = Field(None, description="Race class")
    grade: Optional[str] = Field(None, description="Stakes grade (G1, G2, G3)")

    # Restrictions
    age_restriction: Optional[str] = Field(None, description="Age restriction code")
    age_restriction_description: Optional[str] = Field(None, description="Age restriction")
    sex_restriction: Optional[str] = Field(None, description="Sex restriction code")
    sex_restriction_description: Optional[str] = Field(None, description="Sex restriction")
    race_restriction: Optional[str] = Field(None, description="Race restriction code")
    race_restriction_description: Optional[str] = Field(None, description="Race restriction")

    # Claiming
    min_claim_price: Optional[int] = Field(None, description="Minimum claiming price")
    max_claim_price: Optional[int] = Field(None, description="Maximum claiming price")

    # Purse
    purse: Optional[int] = Field(None, description="Total purse")

    # Breed
    breed: Optional[str] = Field(None, description="Breed (Thoroughbred, Quarter Horse)")

    # Status
    has_finished: Optional[bool] = Field(None, description="Race has finished")
    has_results: Optional[bool] = Field(None, description="Results available")
    is_cancelled: Optional[bool] = Field(None, description="Race cancelled")

    # Changes
    changes: Optional[List[Change]] = Field(None, description="Race changes")

    # Track Info
    track_name: Optional[str] = Field(None, description="Track name")
    time_zone: Optional[str] = Field(None, description="Time zone")
    tote_track_id: Optional[str] = Field(None, description="Tote track ID")
    course_type: Optional[str] = Field(None, description="Course type")
    course_type_class: Optional[str] = Field(None, description="Course type class")

    # Handicapper
    handicapper_name: Optional[str] = Field(None, description="Handicapper name")

    # Pools
    race_pools: Optional[List[RacePool]] = Field(None, description="Betting pools")

    # Runners
    runners: List[Runner] = Field(default_factory=list, description="Horses in race")

    @field_validator('race_pools', mode='before')
    @classmethod
    def validate_race_pools(cls, v: Any) -> List[RacePool]:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @field_validator('changes', mode='before')
    @classmethod
    def validate_changes(cls, v: Any) -> List[Change]:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @field_validator('runners', mode='before')
    @classmethod
    def validate_runners(cls, v: Any) -> List[Runner]:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @computed_field
    @property
    def race_number(self) -> str:
        """Get race number."""
        return self.race_key.race_number

    @computed_field
    @property
    def total_runners(self) -> int:
        """Total number of runners (including scratches)."""
        return len(self.runners)

    @computed_field
    @property
    def active_runners(self) -> int:
        """Number of non-scratched runners."""
        return len([r for r in self.runners if not r.is_scratched])

    @computed_field
    @property
    def scratched_runners(self) -> List[Runner]:
        """Get list of scratched runners."""
        return [r for r in self.runners if r.is_scratched]

    def get_runner_by_program_number(self, program_number: str) -> Optional[Runner]:
        """Get runner by program number."""
        for runner in self.runners:
            if runner.program_number == program_number:
                return runner
        return None

    def get_favorite(self) -> Optional[Runner]:
        """Get the morning line favorite (lowest odds)."""
        active = [r for r in self.runners if not r.is_scratched]
        if not active:
            return None

        # Filter runners with valid odds
        with_odds = [(r, r.get_ml_odds_decimal()) for r in active]
        with_odds = [(r, odds) for r, odds in with_odds if odds is not None]

        if not with_odds:
            return None

        # Return runner with lowest odds
        return min(with_odds, key=lambda x: x[1])[0]