"""Pydantic models for race results."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List, Any, Union

from src.models.result_runner import ResultRunner
from src.models.payoff import Payoff
from src.models.time import RaceFractions


class RaceKey(BaseModel):
    """Race key identifier."""
    race_number: str = Field(..., description="Race number")
    day_evening: Optional[str] = Field(None, description="Day (D) or Evening (E)")


class ResultRace(BaseModel):
    """Race result with finish positions and payoffs."""

    # Identifiers
    race_key: RaceKey = Field(..., description="Race key")

    # Race Details
    age_restriction: Optional[str] = Field(None, description="Age restriction")
    age_restriction_description: Optional[str] = Field(None, description="Age restriction description")
    breed: Optional[str] = Field(None, description="Breed")
    distance_description: Optional[str] = Field(None, description="Distance description")
    distance_unit: Optional[str] = Field(None, description="Distance unit")
    distance_value: Optional[int] = Field(None, description="Distance value")
    grade: Optional[str] = Field(None, description="Stakes grade")
    maximum_claim_price: Optional[str] = Field(None, description="Max claiming price")
    minimum_claim_price: Optional[str] = Field(None, description="Min claiming price")
    race_class: Optional[str] = Field(None, description="Race class")
    race_name: Optional[str] = Field(None, description="Race name")
    race_restriction: Optional[str] = Field(None, description="Race restriction")
    race_restriction_description: Optional[str] = Field(None, description="Race restriction description")
    race_type: Optional[str] = Field(None, description="Race type")
    race_type_description: Optional[str] = Field(None, description="Race type description")
    sex_restriction: Optional[str] = Field(None, description="Sex restriction")
    sex_restriction_description: Optional[str] = Field(None, description="Sex restriction description")
    surface: Optional[str] = Field(None, description="Surface")
    surface_description: Optional[str] = Field(None, description="Surface description")
    total_purse: Optional[str] = Field(None, description="Total purse")
    track_condition_description: Optional[str] = Field(None, description="Track condition")
    track_name: Optional[str] = Field(None, description="Track name")

    # Timing
    off_time: Optional[int] = Field(None, description="Off time (timestamp)")
    post_time: Optional[str] = Field(None, description="Post time")
    post_time_long: Optional[int] = Field(None, description="Post time long format")
    time_zone: Optional[str] = Field(None, description="Time zone")

    # Results
    also_ran: Optional[str] = Field(None, description="Also ran (horses that didn't finish in money)")
    scratches: Optional[List[str]] = Field(None, description="Scratched horses")

    # Times
    fraction: Optional[RaceFractions] = Field(None, description="Fractional times")

    # Payoffs and Wagers
    payoffs: Optional[List[Payoff]] = Field(None, description="All payoffs")
    wager_types: Optional[List] = Field(None, description="Available wager types")

    # Runners
    runners: List[ResultRunner] = Field(default_factory=list, description="Runners with results")

    @field_validator('also_ran', mode='before')
    @classmethod
    def validate_also_ran(cls, v: Any) -> Optional[str]:
        """Handle also_ran as either string or list."""
        if v is None or v == '':
            return None

        # If it's a list, join with commas
        if isinstance(v, list):
            return ', '.join(str(item) for item in v)

        # If it's already a string, return it
        if isinstance(v, str):
            return v

        # Convert anything else to string
        return str(v)

    @field_validator('payoffs', 'scratches', 'wager_types', mode='before')
    @classmethod
    def validate_lists(cls, v: Any) -> List:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @field_validator('runners', mode='before')
    @classmethod
    def validate_runners(cls, v: Any) -> List[ResultRunner]:
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
        """Total runners."""
        return len(self.runners)

    @computed_field
    @property
    def winner(self) -> Optional[ResultRunner]:
        """Get the winning horse (first runner with win payoff)."""
        for runner in self.runners:
            if runner.win_payoff and runner.win_payoff > 0:
                return runner
        # Fallback: first runner
        return self.runners[0] if self.runners else None

    def get_runner_by_program_number(self, program_number: str) -> Optional[ResultRunner]:
        """Get runner by program number."""
        for runner in self.runners:
            if runner.program_number == program_number:
                return runner
        return None

    def get_payoff_by_type(self, wager_type: str) -> Optional[Payoff]:
        """Get payoff by wager type (e.g., 'WN', 'EX', 'TRI')."""
        if not self.payoffs:
            return None

        for payoff in self.payoffs:
            if payoff.wager_type and payoff.wager_type.upper() == wager_type.upper():
                return payoff
        return None

    def get_exotic_payoffs(self) -> List[Payoff]:
        """Get all exotic bet payoffs."""
        if not self.payoffs:
            return []
        return [p for p in self.payoffs if p.is_exotic]