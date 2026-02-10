"""Load entries data from JSON files."""
import json
from pathlib import Path
from typing import Optional
import logging

from sqlalchemy.orm import Session

from src.db.session import get_db_context
from src.db.models import Meet, Race, Runner
from src.db.loaders.helpers import (
    get_or_create_jockey,
    get_or_create_trainer,
    get_or_create_horse,
    parse_surface_type,
    parse_race_type
)
from src.config import settings

logger = logging.getLogger(__name__)


def parse_decimal_odds(odds_str: Optional[str]) -> Optional[float]:
    """
    Parse fractional odds to decimal.

    Examples:
        "5/2" -> 2.5
        "3-1" -> 3.0
        "EVEN" -> 1.0
        "6/5" -> 1.2

    Args:
        odds_str: Odds string

    Returns:
        Decimal odds or None
    """
    if not odds_str:
        return None

    odds_str = str(odds_str).strip().upper()

    if not odds_str or odds_str in ['', 'SCR', 'SCRATCHED']:
        return None

    # Handle special cases
    if odds_str in ['EVEN', 'EVN', '1-1', '1/1']:
        return 1.0

    # Replace dash with slash for consistency
    odds_str = odds_str.replace('-', '/')

    # Parse fraction
    if '/' in odds_str:
        try:
            parts = odds_str.split('/')
            if len(parts) == 2:
                numerator = float(parts[0].strip())
                denominator = float(parts[1].strip())
                if denominator > 0:
                    return numerator / denominator
        except (ValueError, ZeroDivisionError):
            pass

    # Try parsing as decimal
    try:
        return float(odds_str)
    except ValueError:
        pass

    return None


def load_entries_from_json(json_path: Path, db: Session) -> int:
    """
    Load entries from a JSON file.

    Args:
        json_path: Path to JSON file
        db: Database session

    Returns:
        Number of races loaded
    """
    logger.info(f"Loading entries from {json_path.name}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {json_path.name}: {e}")
        return 0

    # Get the meet
    meet_id = data.get('meet_id')
    if not meet_id:
        logger.error(f"No meet_id found in {json_path.name}")
        return 0

    meet = db.query(Meet).filter(Meet.meet_id == meet_id).first()

    if not meet:
        logger.error(f"Meet {meet_id} not found in database. Load meets first.")
        logger.info(f"  File: {json_path.name}")
        return 0

    logger.info(f"  Processing meet: {meet_id}")

    # Update weather if available
    if data.get('weather') and not meet.weather:
        meet.weather = data['weather']

    races_data = data.get('races', [])
    loaded_count = 0

    for race_data in races_data:
        try:
            race_number = race_data['race_key']['race_number']

            # Check if race already exists
            existing_race = db.query(Race).filter(
                Race.meet_id == meet.id,
                Race.race_number == race_number
            ).first()

            if existing_race:
                logger.debug(f"Race {meet_id}-R{race_number} already exists, skipping")
                continue

            # Create race
            race = Race(
                meet_id=meet.id,
                race_number=int(race_number),
                race_name=race_data.get('race_name'),
                post_time=race_data.get('post_time'),
                distance_value=race_data.get('distance_value'),
                distance_unit=race_data.get('distance_unit'),
                distance_description=race_data.get('distance_description'),
                surface=parse_surface_type(race_data.get('surface_description')),
                surface_description=race_data.get('surface_description'),
                track_condition=race_data.get('track_condition'),
                race_type=parse_race_type(race_data.get('race_type_description')),
                race_type_description=race_data.get('race_type_description'),
                race_class=race_data.get('race_class'),
                grade=race_data.get('grade'),
                age_restriction=race_data.get('age_restriction_description'),
                sex_restriction=race_data.get('sex_restriction_description'),
                breed=race_data.get('breed'),
                min_claim_price=race_data.get('min_claim_price'),
                max_claim_price=race_data.get('max_claim_price'),
                purse=race_data.get('purse'),
                has_finished=race_data.get('has_finished', False),
                has_results=race_data.get('has_results', False),
                is_cancelled=race_data.get('is_cancelled', False)
            )

            db.add(race)
            db.flush()  # Get race ID

            # Load runners
            runners_data = race_data.get('runners', [])
            for runner_data in runners_data:
                try:
                    # Get or create horse
                    horse = get_or_create_horse(
                        db,
                        name=runner_data['horse_name'],
                        registration_number=runner_data.get('registration_number'),
                        sire_name=runner_data.get('sire_name'),
                        dam_name=runner_data.get('dam_name'),
                        dam_sire_name=runner_data.get('dam_sire_name')
                    )

                    # Get or create jockey
                    jockey = None
                    if runner_data.get('jockey'):
                        jockey_data = runner_data['jockey']
                        jockey = get_or_create_jockey(
                            db,
                            api_id=jockey_data.get('id'),
                            first_name=jockey_data.get('first_name'),
                            last_name=jockey_data.get('last_name', 'Unknown')
                        )

                    # Get or create trainer
                    trainer = None
                    if runner_data.get('trainer'):
                        trainer_data = runner_data['trainer']
                        trainer = get_or_create_trainer(
                            db,
                            api_id=trainer_data.get('id'),
                            first_name=trainer_data.get('first_name'),
                            last_name=trainer_data.get('last_name', 'Unknown')
                        )

                    # Parse odds
                    ml_decimal = parse_decimal_odds(runner_data.get('morning_line_odds'))
                    live_decimal = parse_decimal_odds(runner_data.get('live_odds'))

                    # Scratch indicator - interpret properly
                    # "N" = Not scratched, "Y" = Scratched
                    scratch_indicator = runner_data.get('scratch_indicator')
                    is_scratched = False  # Default to not scratched

                    if scratch_indicator:
                        scratch_str = str(scratch_indicator).strip().upper()
                        is_scratched = (scratch_str == 'Y')  # Only "Y" means scratched

                    # Create runner
                    runner = Runner(
                        race_id=race.id,
                        horse_id=horse.id,
                        jockey_id=jockey.id if jockey else None,
                        trainer_id=trainer.id if trainer else None,
                        program_number=runner_data['program_number'],
                        program_number_stripped=runner_data.get('program_number_stripped'),
                        post_position=runner_data.get('post_pos'),
                        morning_line_odds=runner_data.get('morning_line_odds'),
                        morning_line_decimal=ml_decimal,
                        live_odds=runner_data.get('live_odds'),
                        live_odds_decimal=live_decimal,
                        weight=int(runner_data['weight']) if runner_data.get('weight') and runner_data[
                            'weight'].isdigit() else None,
                        claiming_price=runner_data.get('claiming'),
                        equipment=runner_data.get('equipment'),
                        medication=runner_data.get('medication'),
                        is_scratched=is_scratched,
                        scratch_indicator=scratch_indicator
                    )

                    db.add(runner)

                except Exception as e:
                    logger.error(f"Error loading runner {runner_data.get('horse_name')}: {e}")
                    # Rollback just this runner, continue with race
                    db.rollback()
                    continue

            loaded_count += 1

        except Exception as e:
            logger.error(f"Error loading race {race_data.get('race_key')}: {e}")
            # Rollback and continue
            db.rollback()
            continue

    logger.info(f"Loaded {loaded_count} new races")
    return loaded_count


def load_all_entries() -> int:
    """
    Load all entries JSON files from data/raw directory.

    Returns:
        Total number of races loaded
    """
    logger.info("Starting entries data load")

    # Find all entries JSON files
    entries_files = list(settings.raw_data_dir.glob("entries_*.json"))

    if not entries_files:
        logger.warning("No entries JSON files found")
        return 0

    logger.info(f"Found {len(entries_files)} entries files")

    total_loaded = 0

    # Process each file in its own transaction
    for json_file in entries_files:
        try:
            # Each file gets its own database session
            with get_db_context() as db:
                count = load_entries_from_json(json_file, db)
                total_loaded += count
        except Exception as e:
            logger.error(f"Error processing {json_file.name}: {e}")
            # Continue to next file even if this one fails
            continue

    logger.info(f"✓ Total races loaded: {total_loaded}")
    return total_loaded


if __name__ == "__main__":
    from src.utils.logger import setup_logging

    setup_logging("load_entries")

    total = load_all_entries()
    print(f"\n✓ Loaded {total} races with entries into database")