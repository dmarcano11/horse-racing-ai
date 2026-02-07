"""Pydantic models for betting payoffs."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, Any
from decimal import Decimal


class Payoff(BaseModel):
    """Individual betting payoff."""

    base_amount: Optional[float] = Field(None, description="Base bet amount (usually 2 for $2)")
    carryover: Optional[float] = Field(None, description="Carryover amount")
    number_of_rights: Optional[int] = Field(None, description="Number of winning tickets")
    number_of_tickets_bet: Optional[int] = Field(None, description="Total tickets bet")
    payoff_amount: Optional[float] = Field(None, description="Payoff amount for base bet")
    total_pool: Optional[float] = Field(None, description="Total pool amount")
    wager_name: Optional[str] = Field(None, description="Wager name (e.g., 'Win', 'Exacta')")
    wager_type: Optional[str] = Field(None, description="Wager type code (e.g., 'WN', 'EX')")
    winning_numbers: Optional[str] = Field(None, description="Winning numbers (e.g., '1-3-5')")

    @field_validator('base_amount', 'carryover', 'payoff_amount', 'total_pool', mode='before')
    @classmethod
    def validate_float_fields(cls, v: Any) -> Optional[float]:
        """Handle comma-separated numbers and empty strings."""
        if v == '' or v is None:
            return None

        # If already a number, return it
        if isinstance(v, (int, float)):
            return float(v)

        # If string, remove commas and convert
        if isinstance(v, str):
            try:
                # Remove commas and whitespace
                cleaned = v.replace(',', '').strip()
                return float(cleaned)
            except (ValueError, AttributeError):
                return None

        return None

    @computed_field
    @property
    def is_exotic(self) -> bool:
        """Check if this is an exotic bet (not win/place/show)."""
        if not self.wager_type:
            return False
        return self.wager_type.upper() not in ['WN', 'PL', 'SH', 'WIN', 'PLACE', 'SHOW']

    @computed_field
    @property
    def profit(self) -> Optional[Decimal]:
        """Calculate profit (payoff - base_amount)."""
        if self.payoff_amount is None or self.base_amount is None:
            return None
        return Decimal(str(self.payoff_amount)) - Decimal(str(self.base_amount))

    @computed_field
    @property
    def roi_percentage(self) -> Optional[Decimal]:
        """Calculate ROI percentage."""
        if self.profit is None or self.base_amount is None or self.base_amount == 0:
            return None
        return (self.profit / Decimal(str(self.base_amount))) * Decimal(100)

    def get_winning_numbers_list(self) -> list[str]:
        """Parse winning numbers string into list."""
        if not self.winning_numbers:
            return []

        # Handle different formats: "1-3-5", "1/3/5", "1,3,5"
        separators = ['-', '/', ',', ' ']
        for sep in separators:
            if sep in self.winning_numbers:
                return [num.strip() for num in self.winning_numbers.split(sep)]

        # Single number
        return [self.winning_numbers.strip()]

    class Config:
        json_schema_extra = {
            "example": {
                "wager_type": "EX",
                "wager_name": "Exacta",
                "winning_numbers": "1-3",
                "payoff_amount": 45.80,
                "base_amount": 2
            }
        }