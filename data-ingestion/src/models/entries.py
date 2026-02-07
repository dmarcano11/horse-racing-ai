"""Pydantic models for meet entries endpoint."""
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional, Any, Union

from src.models.race import Race


class Weather(BaseModel):
    """Weather information for the meet."""

    forecast_weather_description: Optional[str] = Field(None, description="Forecast description")
    forecast_high: Optional[int] = Field(None, description="Forecast high temperature")
    forecast_low: Optional[int] = Field(None, description="Forecast low temperature")
    forecast_precipitation: Optional[int] = Field(None, description="Precipitation chance")
    current_weather_description: Optional[str] = Field(None, description="Current weather")

    @field_validator('forecast_high', 'forecast_low', 'forecast_precipitation', mode='before')
    @classmethod
    def validate_int_fields(cls, v: Any) -> Optional[int]:
        """Convert empty strings to None for integer fields."""
        if v == '' or v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class EntriesResponse(BaseModel):
    """Response from /meets/{meet_id}/entries endpoint."""

    meet_id: str = Field(..., description="Meet ID")
    track_id: Optional[str] = Field(None, description="Track ID")
    track_name: str = Field(..., description="Track name")
    country: Optional[str] = Field(None, description="Country")
    date: str = Field(..., description="Meet date")

    races: List[Race] = Field(default_factory=list, description="Races")
    weather: Optional[Weather] = Field(None, description="Weather")

    @field_validator('races', mode='before')
    @classmethod
    def validate_races(cls, v: Any) -> List[Race]:
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
    def total_runners(self) -> int:
        """Total runners across all races."""
        return sum(race.total_runners for race in self.races)

    def get_race(self, race_number: str) -> Optional[Race]:
        """Get race by race number."""
        for race in self.races:
            if race.race_number == race_number:
                return race
        return None

    def get_races_by_surface(self, surface: str) -> List[Race]:
        """Get races by surface type."""
        return [
            race for race in self.races
            if race.surface_description and surface.lower() in race.surface_description.lower()
        ]