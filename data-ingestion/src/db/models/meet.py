"""Meet model."""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Meet(Base):
    """Race meeting (card)."""

    __tablename__ = "meets"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    meet_id = Column(String(50), unique=True, nullable=False, index=True)
    track_id = Column(Integer, ForeignKey('racing.tracks.id'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    weather = Column(JSON)  # Store weather as JSON

    # Relationships
    track = relationship("Track", back_populates="meets")
    races = relationship("Race", back_populates="meet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meet(meet_id='{self.meet_id}', date='{self.date}')>"