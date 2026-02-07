"""Person models (jockey, trainer, owner)."""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from src.db.base import Base


class Jockey(Base):
    """Jockey."""

    __tablename__ = "jockeys"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(String(50), unique=True, index=True)  # ID from API
    first_name = Column(String(50))
    last_name = Column(String(50), nullable=False, index=True)
    middle_name = Column(String(50))

    # Relationships
    runners = relationship("Runner", back_populates="jockey")

    def __repr__(self):
        return f"<Jockey(name='{self.first_name} {self.last_name}')>"


class Trainer(Base):
    """Trainer."""

    __tablename__ = "trainers"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50), nullable=False, index=True)
    middle_name = Column(String(50))

    # Relationships
    runners = relationship("Runner", back_populates="trainer")

    def __repr__(self):
        return f"<Trainer(name='{self.first_name} {self.last_name}')>"


class Owner(Base):
    """Owner."""

    __tablename__ = "owners"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)

    # Relationships
    horses = relationship("Horse", secondary="racing.horse_owners", back_populates="owners")

    def __repr__(self):
        return f"<Owner(name='{self.name}')>"