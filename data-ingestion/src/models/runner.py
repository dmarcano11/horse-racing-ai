"""Pydantic models for race runners (horses)."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List, Any
from decimal import Decimal

from src.models.person import Jockey, Trainer
from src.models.pools import HorseDataPool


class Runner(BaseModel):
    """Individual horse/runner in a race."""

    # Basic Info
    horse_name: str = Field(..., description="Horse name")
    program_number: str = Field(..., description="Program number (can be '1A' for coupled)")
    program_number_stripped: Optional[int] = Field(None, description="Program number as integer")
    post_pos: Optional[str] = Field(None, description="Post position")
    registration_number: Optional[str] = Field(None, description="Horse registration number")

    # People
    jockey: Optional[Jockey] = Field(None, description="Jockey information")
    trainer: Optional[Trainer] = Field(None, description="Trainer information")

    # Odds
    morning_line_odds: Optional[str] = Field(None, description="Morning line odds")
    live_odds: Optional[str] = Field(None, description="Live odds")
    horse_data_pools: Optional[List[HorseDataPool]] = Field(None, description="Pool data")

    # Breeding
    sire_name: Optional[str] = Field(None, description="Sire (father)")
    dam_name: Optional[str] = Field(None, description="Dam (mother)")
    dam_sire_name: Optional[str] = Field(None, description="Dam's sire")

    # Race Conditions
    weight: Optional[str] = Field(None, description="Weight carried")
    claiming: Optional[int] = Field(None, description="Claiming price")
    equipment: Optional[str] = Field(None, description="Equipment (blinkers, etc.)")
    medication: Optional[str] = Field(None, description="Medication (Lasix, etc.)")

    # Status
    scratch_indicator: Optional[str] = Field(None, description="Scratch indicator")
    coupled_type: Optional[str] = Field(None, description="Coupled entry type")
    description: Optional[str] = Field(None, description="Additional description")

    @field_validator('horse_data_pools', mode='before')
    @classmethod
    def validate_horse_data_pools(cls, v: Any) -> List[HorseDataPool]:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @computed_field
    @property
    def is_scratched(self) -> bool:
        """Check if horse is scratched."""
        return bool(self.scratch_indicator and self.scratch_indicator.strip())

    @computed_field
    @property
    def is_coupled(self) -> bool:
        """Check if horse is part of coupled entry."""
        return bool(self.coupled_type)

    def get_ml_odds_decimal(self) -> Optional[Decimal]:
        """Convert morning line odds to decimal."""
        if not self.morning_line_odds:
            return None

        try:
            # Handle fractional odds (e.g., "5/2")
            if '/' in self.morning_line_odds:
                num, denom = self.morning_line_odds.split('/')
                return Decimal(num) / Decimal(denom)
            # Handle decimal odds
            return Decimal(self.morning_line_odds)
        except (ValueError, ZeroDivisionError):
            return None

    def get_live_odds_decimal(self) -> Optional[Decimal]:
        """Convert live odds to decimal."""
        if not self.live_odds:
            return None

        try:
            if '/' in self.live_odds:
                num, denom = self.live_odds.split('/')
                return Decimal(num) / Decimal(denom)
            return Decimal(self.live_odds)
        except (ValueError, ZeroDivisionError):
            return None

    class Config:
        json_schema_extra = {
            "example": {
                "horse_name": "Fast Horse",
                "program_number": "1",
                "jockey": {"first_name": "John", "last_name": "Smith"},
                "trainer": {"first_name": "Jane", "last_name": "Doe"},
                "morning_line_odds": "5/2",
                "weight": "122"
            }
        }