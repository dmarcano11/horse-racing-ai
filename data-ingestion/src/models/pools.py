"""Pydantic models for betting pools."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Union


class HorseDataPool(BaseModel):
    """Individual pool data for a horse (odds)."""

    pool_type_name: Optional[str] = Field(None, description="Pool type (e.g., 'Win')")
    amount: Optional[str] = Field(None, description="Pool amount")
    fractional_odds: Optional[str] = Field(None, description="Fractional odds (e.g., '5/2')")
    dollar: Optional[str] = Field(None, description="Dollar odds")


class RacePool(BaseModel):
    """Betting pool configuration for a race."""

    maximum_wager_amount: Optional[float] = Field(None, description="Max wager in dollars")
    minimum_box_amount: Optional[float] = Field(None, description="Min box amount in dollars")
    minimum_wager_amount: Optional[float] = Field(None, description="Min wager in dollars")
    minimum_wheel_amount: Optional[float] = Field(None, description="Min wheel amount in dollars")
    pool_code: Optional[str] = Field(None, description="Pool code")
    pool_name: Optional[str] = Field(None, description="Pool name (e.g., 'Win', 'Exacta')")
    race_list: Optional[str] = Field(None, description="Races included in pool")

    @field_validator('maximum_wager_amount', 'minimum_box_amount', 'minimum_wager_amount', 'minimum_wheel_amount', mode='before')
    @classmethod
    def validate_float_fields(cls, v: Any) -> Optional[float]:
        """Convert various types to float, handle empty strings."""
        if v == '' or v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None