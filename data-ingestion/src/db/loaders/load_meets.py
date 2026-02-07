"""Load meets data from JSON files."""
import json
from pathlib import Path
from datetime import datetime
from typing import List
import logging

from sqlalchemy.orm import Session

from src.db.session import get_db_context
from src.db.models import Meet, Track
from src.db.loaders.helpers import get_or_create_track
from src.config import settings

logger = logging.getLogger(__name__)


def load_meets_from_json(json_path: Path, db: Session) -> int:
    """
    Load meets from a JSON file.

    Args:
        json_path: Path to JSON file
        db: Database session

    Returns:
        Number of meets loaded
    """
    logger.info(f"Loading meets from {json_path.name}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meets_data = data.get('meets', [])
    loaded_count = 0

    for meet_data in meets_data:
        try:
            # Get or create track
            track = get_or_create_track(
                db,
                track_id=meet_data['track_id'],
                track_name=meet_data['track_name'],
                country=meet_data.get('country')
            )

            # Check if meet already exists
            existing_meet = db.query(Meet).filter(
                Meet.meet_id == meet_data['meet_id']
            ).first()

            if existing_meet:
                logger.debug(f"Meet {meet_data['meet_id']} already exists, skipping")
                continue

            # Parse date
            try:
                meet_date = datetime.strptime(meet_data['date'], '%Y-%m-%d').date()
            except ValueError:
                logger.error(f"Invalid date format: {meet_data['date']}")
                continue

            # Create meet
            meet = Meet(
                meet_id=meet_data['meet_id'],
                track_id=track.id,
                date=meet_date,
                weather=None  # We'll update this when loading entries
            )

            db.add(meet)
            loaded_count += 1

        except Exception as e:
            logger.error(f"Error loading meet {meet_data.get('meet_id')}: {e}")
            continue

    db.flush()
    logger.info(f"Loaded {loaded_count} new meets")
    return loaded_count


def load_all_meets() -> int:
    """
    Load all meets JSON files from data/raw directory.

    Returns:
        Total number of meets loaded
    """
    logger.info("Starting meets data load")

    # Find all meets JSON files
    meets_files = list(settings.raw_data_dir.glob("meets_*.json"))

    if not meets_files:
        logger.warning("No meets JSON files found")
        return 0

    logger.info(f"Found {len(meets_files)} meets files")

    total_loaded = 0

    with get_db_context() as db:
        for json_file in meets_files:
            try:
                count = load_meets_from_json(json_file, db)
                total_loaded += count
            except Exception as e:
                logger.error(f"Error processing {json_file.name}: {e}")
                continue

    logger.info(f"✓ Total meets loaded: {total_loaded}")
    return total_loaded


if __name__ == "__main__":
    from src.utils.logger import setup_logging

    setup_logging("load_meets")

    total = load_all_meets()
    print(f"\n✓ Loaded {total} meets into database")