"""Pydantic models for meet results endpoint."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional, Any

from src.models.result_race import ResultRace


class Weather(BaseModel):
    """Weather information."""

    current_temperature: Optional[str] = Field(None, description="Current temperature")
    current_weather_description: Optional[str] = Field(None, description="Current weather")
    date: Optional[str] = Field(None, description="Date")
    forecast_high: Optional[int] = Field(None, description="Forecast high")
    forecast_low: Optional[int] = Field(None, description="Forecast low")
    forecast_precipitation: Optional[int] = Field(None, description="Forecast precipitation")
    forecast_weather_description: Optional[str] = Field(None, description="Forecast weather")

    @field_validator('forecast_high', 'forecast_low', 'forecast_precipitation', mode='before')
    @classmethod
    def validate_int_fields(cls, v: Any) -> Optional[int]:
        """Convert empty strings to None."""
        if v == '' or v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class ResultsResponse(BaseModel):
    """Response from /meets/{meet_id}/results endpoint."""

    meet_id: str = Field(..., description="Meet ID")
    track_id: Optional[str] = Field(None, description="Track ID")
    track_name: str = Field(..., description="Track name")
    country: Optional[str] = Field(None, description="Country")
    date: str = Field(..., description="Meet date")

    races: List[ResultRace] = Field(default_factory=list, description="Race results")
    weather: Optional[Weather] = Field(None, description="Weather")

    @field_validator('races', mode='before')
    @classmethod
    def validate_races(cls, v: Any) -> List[ResultRace]:
        """Convert None to empty list."""
        if v is None:
            return []
        return v

    @computed_field
    @property
    def total_races(self) -> int:
        """Total number of races."""
        return len(self.races)

    @computed_field
    @property
    def completed_races(self) -> int:
        """Number of races with results."""
        return len([r for r in self.races if r.runners])

    def get_race(self, race_number: str) -> Optional[ResultRace]:
        """Get race by race number."""
        for race in self.races:
            if race.race_number == race_number:
                return race
        return None