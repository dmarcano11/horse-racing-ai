"""Helper functions for data loading."""
from sqlalchemy.orm import Session
from typing import Optional
import logging

from src.db.models import Jockey, Trainer, Horse, Track

logger = logging.getLogger(__name__)


def get_or_create_jockey(
        db: Session,
        api_id: Optional[str],
        first_name: Optional[str],
        last_name: str
) -> Jockey:
    """
    Get existing jockey or create new one.

    Args:
        db: Database session
        api_id: API ID
        first_name: First name
        last_name: Last name

    Returns:
        Jockey instance
    """
    # Try to find by API ID first
    if api_id:
        jockey = db.query(Jockey).filter(Jockey.api_id == api_id).first()
        if jockey:
            return jockey

    # Try to find by name
    jockey = db.query(Jockey).filter(
        Jockey.first_name == first_name,
        Jockey.last_name == last_name
    ).first()

    if jockey:
        # Update API ID if we have it
        if api_id and not jockey.api_id:
            jockey.api_id = api_id
            db.flush()
        return jockey

    # Create new jockey
    jockey = Jockey(
        api_id=api_id,
        first_name=first_name,
        last_name=last_name
    )
    db.add(jockey)
    db.flush()  # Get the ID
    logger.debug(f"Created new jockey: {first_name} {last_name}")
    return jockey


def get_or_create_trainer(
        db: Session,
        api_id: Optional[str],
        first_name: Optional[str],
        last_name: str
) -> Trainer:
    """
    Get existing trainer or create new one.

    Args:
        db: Database session
        api_id: API ID
        first_name: First name
        last_name: Last name

    Returns:
        Trainer instance
    """
    # Try to find by API ID first
    if api_id:
        trainer = db.query(Trainer).filter(Trainer.api_id == api_id).first()
        if trainer:
            return trainer

    # Try to find by name
    trainer = db.query(Trainer).filter(
        Trainer.first_name == first_name,
        Trainer.last_name == last_name
    ).first()

    if trainer:
        # Update API ID if we have it
        if api_id and not trainer.api_id:
            trainer.api_id = api_id
            db.flush()
        return trainer

    # Create new trainer
    trainer = Trainer(
        api_id=api_id,
        first_name=first_name,
        last_name=last_name
    )
    db.add(trainer)
    db.flush()
    logger.debug(f"Created new trainer: {first_name} {last_name}")
    return trainer


def get_or_create_horse(
        db: Session,
        name: str,
        registration_number: Optional[str] = None,
        sire_name: Optional[str] = None,
        dam_name: Optional[str] = None,
        dam_sire_name: Optional[str] = None,
        breed: Optional[str] = None
) -> Horse:
    """
    Get existing horse or create new one.

    Args:
        db: Database session
        name: Horse name
        registration_number: Registration number
        sire_name: Sire name
        dam_name: Dam name
        dam_sire_name: Dam sire name
        breed: Breed

    Returns:
        Horse instance
    """
    # Try to find by registration number
    if registration_number:
        horse = db.query(Horse).filter(
            Horse.registration_number == registration_number
        ).first()
        if horse:
            return horse

    # Try to find by name (horses can have same names, but we'll assume uniqueness for now)
    horse = db.query(Horse).filter(Horse.name == name).first()

    if horse:
        # Update additional info if we have it
        if registration_number and not horse.registration_number:
            horse.registration_number = registration_number
        if sire_name and not horse.sire_name:
            horse.sire_name = sire_name
        if dam_name and not horse.dam_name:
            horse.dam_name = dam_name
        if dam_sire_name and not horse.dam_sire_name:
            horse.dam_sire_name = dam_sire_name
        if breed and not horse.breed:
            horse.breed = breed
        db.flush()
        return horse

    # Create new horse
    horse = Horse(
        name=name,
        registration_number=registration_number,
        sire_name=sire_name,
        dam_name=dam_name,
        dam_sire_name=dam_sire_name,
        breed=breed
    )
    db.add(horse)
    db.flush()
    logger.debug(f"Created new horse: {name}")
    return horse


def get_or_create_track(
        db: Session,
        track_id: str,
        track_name: str,
        country: Optional[str] = None
) -> Track:
    """
    Get existing track or create new one.

    Args:
        db: Database session
        track_id: Track ID
        track_name: Track name
        country: Country

    Returns:
        Track instance
    """
    track = db.query(Track).filter(Track.track_id == track_id).first()

    if track:
        return track

    # Create new track
    track = Track(
        track_id=track_id,
        track_name=track_name,
        country=country
    )
    db.add(track)
    db.flush()
    logger.info(f"Created new track: {track_name}")
    return track


def parse_surface_type(surface_desc: Optional[str]) -> str:
    """
    Parse surface description to SurfaceType enum.

    Args:
        surface_desc: Surface description from API

    Returns:
        SurfaceType value
    """
    if not surface_desc:
        return "Unknown"

    surface_lower = surface_desc.lower()

    if 'dirt' in surface_lower:
        return "Dirt"
    elif 'turf' in surface_lower or 'grass' in surface_lower:
        return "Turf"
    elif 'synthetic' in surface_lower or 'tapeta' in surface_lower or 'polytrack' in surface_lower:
        return "Synthetic"
    else:
        return "Unknown"


def parse_race_type(race_type_desc: Optional[str]) -> str:
    """
    Parse race type description to RaceType enum.

    Args:
        race_type_desc: Race type description from API

    Returns:
        RaceType value
    """
    if not race_type_desc:
        return "Unknown"

    type_lower = race_type_desc.lower()

    if 'maiden' in type_lower:
        return "Maiden"
    elif 'claiming' in type_lower:
        return "Claiming"
    elif 'allowance' in type_lower:
        return "Allowance"
    elif 'stakes' in type_lower:
        return "Stakes"
    elif 'handicap' in type_lower:
        return "Handicap"
    else:
        return "Unknown"