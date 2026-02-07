"""Pydantic models for race result runners."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, Any


class ResultRunner(BaseModel):
    """Runner result information."""

    # Basic Info
    breeder_name: Optional[str] = Field(None, description="Breeder name")
    horse_name: str = Field(..., description="Horse name")

    # People
    jockey_first_name: Optional[str] = Field(None, description="Jockey first name")
    jockey_first_name_initial: Optional[str] = Field(None, description="Jockey first initial")
    jockey_last_name: Optional[str] = Field(None, description="Jockey last name")
    owner_first_name: Optional[str] = Field(None, description="Owner first name")
    owner_last_name: Optional[str] = Field(None, description="Owner last name")
    trainer_first_name: Optional[str] = Field(None, description="Trainer first name")
    trainer_last_name: Optional[str] = Field(None, description="Trainer last name")

    # Program Info
    program_number: str = Field(..., description="Program number")
    program_number_stripped: Optional[int] = Field(None, description="Program number as integer")

    # Payoffs
    place_payoff: Optional[float] = Field(None, description="Place payoff")
    show_payoff: Optional[float] = Field(None, description="Show payoff")
    win_payoff: Optional[float] = Field(None, description="Win payoff")

    # Breeding
    sire_name: Optional[str] = Field(None, description="Sire name")

    # Race Details
    weight_carried: Optional[str] = Field(None, description="Weight carried")

    @field_validator('place_payoff', 'show_payoff', 'win_payoff', mode='before')
    @classmethod
    def validate_payoff(cls, v: Any) -> Optional[float]:
        """Handle various payoff formats."""
        if v == '' or v is None or v == 0:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @computed_field
    @property
    def jockey_name(self) -> str:
        """Get jockey full name."""
        parts = []
        if self.jockey_first_name:
            parts.append(self.jockey_first_name)
        if self.jockey_last_name:
            parts.append(self.jockey_last_name)
        return " ".join(parts) if parts else "Unknown"

    @computed_field
    @property
    def trainer_name(self) -> str:
        """Get trainer full name."""
        parts = []
        if self.trainer_first_name:
            parts.append(self.trainer_first_name)
        if self.trainer_last_name:
            parts.append(self.trainer_last_name)
        return " ".join(parts) if parts else "Unknown"

    @computed_field
    @property
    def has_payoff(self) -> bool:
        """Check if horse has any payoff."""
        return any([
            self.win_payoff,
            self.place_payoff,
            self.show_payoff
        ])