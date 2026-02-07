"""Pydantic models for race times."""
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from decimal import Decimal, InvalidOperation


class FractionalTime(BaseModel):
    """Time for a fractional point in the race."""

    minutes: Optional[int] = Field(None, description="Minutes")
    seconds: Optional[int] = Field(None, description="Seconds")
    hundredths: Optional[int] = Field(None, description="Hundredths of a second")
    milliseconds: Optional[int] = Field(None, description="Milliseconds")
    fifths: Optional[int] = Field(None, description="Fifths of a second")
    str_fifths: Optional[str] = Field(None, description="String representation in fifths")
    time_in_fifths: Optional[str] = Field(None, description="Time in fifths format")
    time_in_hundredths: Optional[str] = Field(None, description="Time in hundredths format")

    @computed_field
    @property
    def total_seconds(self) -> Optional[Decimal]:
        """Convert time to total seconds as decimal."""
        if self.time_in_hundredths:
            try:
                # Parse format like "22.45" or "1:10.25"
                time_str = self.time_in_hundredths.strip()

                # Skip if empty
                if not time_str:
                    return None

                if ':' in time_str:
                    # Format: "1:10.25" (minutes:seconds.hundredths)
                    parts = time_str.split(':')
                    if len(parts) == 2 and parts[0] and parts[1]:
                        minutes = Decimal(parts[0])
                        seconds = Decimal(parts[1])
                        return minutes * 60 + seconds
                else:
                    # Format: "22.45" (seconds.hundredths)
                    return Decimal(time_str)
            except (ValueError, IndexError, InvalidOperation):
                # If parsing fails, try fallback method
                pass

        # Fallback: calculate from components
        try:
            if self.minutes is not None and self.seconds is not None:
                total = Decimal(self.minutes * 60 + self.seconds)
                if self.hundredths is not None:
                    total += Decimal(self.hundredths) / Decimal(100)
                return total
        except (ValueError, InvalidOperation):
            pass

        return None

    def __str__(self) -> str:
        """String representation."""
        return self.time_in_hundredths or self.time_in_fifths or "N/A"


class RaceFractions(BaseModel):
    """Fractional times for a race."""

    fraction_1: Optional[FractionalTime] = Field(None, description="First call (e.g., 2 furlongs)")
    fraction_2: Optional[FractionalTime] = Field(None, description="Second call (e.g., 4 furlongs)")
    fraction_3: Optional[FractionalTime] = Field(None, description="Third call")
    fraction_4: Optional[FractionalTime] = Field(None, description="Fourth call")
    fraction_5: Optional[FractionalTime] = Field(None, description="Fifth call")
    winning_time: Optional[FractionalTime] = Field(None, description="Final winning time")

    @computed_field
    @property
    def has_fractions(self) -> bool:
        """Check if any fractional times exist."""
        return any([
            self.fraction_1,
            self.fraction_2,
            self.fraction_3,
            self.fraction_4,
            self.fraction_5,
            self.winning_time
        ])

    def get_all_fractions(self) -> list[Optional[FractionalTime]]:
        """Get list of all fractional times in order."""
        return [
            self.fraction_1,
            self.fraction_2,
            self.fraction_3,
            self.fraction_4,
            self.fraction_5
        ]