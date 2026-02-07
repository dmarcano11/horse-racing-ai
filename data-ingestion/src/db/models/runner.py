"""Runner model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.db.base import Base


class Runner(Base):
    """Horse entry in a race."""

    __tablename__ = "runners"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('racing.races.id'), nullable=False, index=True)
    horse_id = Column(Integer, ForeignKey('racing.horses.id'), nullable=False, index=True)
    jockey_id = Column(Integer, ForeignKey('racing.jockeys.id'), index=True)
    trainer_id = Column(Integer, ForeignKey('racing.trainers.id'), index=True)

    # Program Info
    program_number = Column(String(10), nullable=False)
    program_number_stripped = Column(Integer)
    post_position = Column(String(10))

    # Odds
    morning_line_odds = Column(String(20))
    morning_line_decimal = Column(Float)
    live_odds = Column(String(20))
    live_odds_decimal = Column(Float)

    # Weight and Claiming
    weight = Column(Integer)
    claiming_price = Column(Integer)

    # Equipment and Medication
    equipment = Column(String(100))
    medication = Column(String(50))

    # Status
    is_scratched = Column(Boolean, default=False)
    is_coupled = Column(Boolean, default=False)
    scratch_indicator = Column(String(10))

    # Relationships
    race = relationship("Race", back_populates="runners")
    horse = relationship("Horse", back_populates="runners")
    jockey = relationship("Jockey", back_populates="runners")
    trainer = relationship("Trainer", back_populates="runners")
    result = relationship("RunnerResult", back_populates="runner", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Runner(id={self.id}, program_number='{self.program_number}')>"