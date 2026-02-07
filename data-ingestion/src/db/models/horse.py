"""Horse model."""
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base

# Association table for horse-owner many-to-many relationship
horse_owners = Table(
    'horse_owners',
    Base.metadata,
    Column('horse_id', Integer, ForeignKey('racing.horses.id'), primary_key=True),
    Column('owner_id', Integer, ForeignKey('racing.owners.id'), primary_key=True),
    schema='racing'
)


class Horse(Base):
    """Horse."""

    __tablename__ = "horses"
    __table_args__ = {'schema': 'racing'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    registration_number = Column(String(50), unique=True, index=True)

    # Breeding
    sire_name = Column(String(100))
    dam_name = Column(String(100))
    dam_sire_name = Column(String(100))
    breeder_name = Column(String(200))

    # Breed
    breed = Column(String(50))  # Thoroughbred, Quarter Horse, etc.

    # Relationships
    runners = relationship("Runner", back_populates="horse")
    owners = relationship("Owner", secondary=horse_owners, back_populates="horses")

    def __repr__(self):
        return f"<Horse(name='{self.name}')>"