"""Race result model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class RaceResult(Base):
    """Race result with fractional times."""

    __tablename__ = "race_results"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('racing.races.id'), nullable=False, unique=True, index=True)

    # Times (stored as JSON for flexibility)
    fractional_times = Column(JSON)  # Store all fractions
    winning_time_seconds = Column(Float)

    # Additional info
    also_ran = Column(String(500))  # Horses that didn't finish in money

    # Relationship
    race = relationship("Race", back_populates="result")
    runner_results = relationship("RunnerResult", back_populates="race_result", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RaceResult(race_id={self.race_id})>"