"""Pydantic models for people (jockeys, trainers, owners)."""
from pydantic import BaseModel, Field
from typing import Optional

class Person(BaseModel):
    """Base model for a person (jockey, trainer, owner)."""

    id: Optional[str] = Field(None, description="Unique identifier")
    alias: Optional[str] = Field(None, description="Alias or nickname")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    type: Optional[str] = Field(None, description="Person type")

    @property
    def full_name(self) -> str:
        """Get full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.alias or "Unknown"

    @property
    def display_name(self) -> str:
        """Get display name (First Initial. Last Name)."""
        if self.first_name_initial and self.last_name:
            return f"{self.first_name_initial}. {self.last_name}"
        return self.full_name

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123456",
                "first_name": "John",
                "first_name_initial": "J",
                "last_name": "Smith",
                "type": "jockey"
            }
        }


class Jockey(Person):
    """Jockey model (extends Person)."""
    pass


class Trainer(Person):
    """Trainer model (extends Person)."""
    pass


class Owner(Person):
    """Owner model (extends Person)."""
    pass