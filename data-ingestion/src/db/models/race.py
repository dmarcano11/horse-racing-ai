"""Race model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from src.db.base import Base
import enum


class SurfaceType(str, enum.Enum):
    """Surface types."""
    DIRT = "Dirt"
    TURF = "Turf"
    SYNTHETIC = "Synthetic"
    UNKNOWN = "Unknown"


class RaceType(str, enum.Enum):
    """Race types."""
    MAIDEN = "Maiden"
    CLAIMING = "Claiming"
    ALLOWANCE = "Allowance"
    STAKES = "Stakes"
    HANDICAP = "Handicap"
    UNKNOWN = "Unknown"


class Race(Base):
    """Individual race."""

    __tablename__ = "races"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    meet_id = Column(Integer, ForeignKey('racing.meets.id'), nullable=False, index=True)

    # Race Identification
    race_number = Column(Integer, nullable=False)
    race_name = Column(String(200))

    # Timing
    post_time = Column(String(20))
    post_time_dt = Column(DateTime)
    off_time = Column(Integer)  # Actual start time (timestamp)

    # Distance
    distance_value = Column(Integer)  # Distance value (e.g., 6 for 6 furlongs)
    distance_unit = Column(String(20))  # Furlongs, Miles, Yards
    distance_description = Column(String(50))

    # Surface and Conditions
    surface = Column(SQLEnum(SurfaceType), default=SurfaceType.UNKNOWN)
    surface_description = Column(String(50))
    track_condition = Column(String(50))

    # Classification
    race_type = Column(SQLEnum(RaceType), default=RaceType.UNKNOWN)
    race_type_description = Column(String(100))
    race_class = Column(String(50))
    grade = Column(String(10))  # G1, G2, G3 for stakes

    # Restrictions
    age_restriction = Column(String(50))
    sex_restriction = Column(String(50))
    breed = Column(String(50))

    # Claiming
    min_claim_price = Column(Integer)
    max_claim_price = Column(Integer)

    # Purse
    purse = Column(Integer)

    # Status
    has_finished = Column(Boolean, default=False)
    has_results = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)

    # Relationships
    meet = relationship("Meet", back_populates="races")
    runners = relationship("Runner", back_populates="race", cascade="all, delete-orphan")
    result = relationship("RaceResult", back_populates="race", uselist=False, cascade="all, delete-orphan")
    payoffs = relationship("Payoff", back_populates="race", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Race(id={self.id}, race_number={self.race_number})>"