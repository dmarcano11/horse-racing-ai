"""Track model."""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from src.db.base import Base


class Track(Base):
    """Racing track."""

    __tablename__ = "tracks"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(String(10), unique=True, nullable=False, index=True)
    track_name = Column(String(100), nullable=False)
    country = Column(String(10))

    # Relationships
    meets = relationship("Meet", back_populates="track", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Track(track_id='{self.track_id}', name='{self.track_name}')>"