"""Payoff model."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base


class Payoff(Base):
    """Betting payoff."""

    __tablename__ = "payoffs"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('racing.races.id'), nullable=False, index=True)

    # Wager Info
    wager_type = Column(String(10), nullable=False)  # WN, PL, SH, EX, TRI, etc.
    wager_name = Column(String(50))  # Win, Place, Exacta, etc.
    winning_numbers = Column(String(50))  # e.g., "1-3-5"

    # Amounts
    base_amount = Column(Float)  # Usually 2.00
    payoff_amount = Column(Float)
    total_pool = Column(Float)

    # Additional Info
    number_of_winning_tickets = Column(Integer)
    carryover = Column(Float)

    # Relationship
    race = relationship("Race", back_populates="payoffs")

    def __repr__(self):
        return f"<Payoff(wager_type='{self.wager_type}', amount={self.payoff_amount})>"