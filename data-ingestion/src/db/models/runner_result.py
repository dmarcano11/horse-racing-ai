"""Runner result model."""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base


class RunnerResult(Base):
    """Individual runner's race result."""

    __tablename__ = "runner_results"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    runner_id = Column(Integer, ForeignKey('racing.runners.id'), nullable=False, unique=True, index=True)
    race_result_id = Column(Integer, ForeignKey('racing.race_results.id'), nullable=False, index=True)

    # Finish Position
    finish_position = Column(Integer)  # 1 = winner, 2 = second, etc.

    # Payoffs
    win_payoff = Column(Float)
    place_payoff = Column(Float)
    show_payoff = Column(Float)

    # Relationships
    runner = relationship("Runner", back_populates="result")
    race_result = relationship("RaceResult", back_populates="runner_results")

    def __repr__(self):
        return f"<RunnerResult(runner_id={self.runner_id}, position={self.finish_position})>"