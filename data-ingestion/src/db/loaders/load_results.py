"""Load results data from JSON files."""
import json
from pathlib import Path
from typing import Optional
import logging

from sqlalchemy.orm import Session

from src.db.session import get_db_context
from src.db.models import Race, Runner, RaceResult, RunnerResult, Payoff
from src.config import settings

logger = logging.getLogger(__name__)


def load_results_from_json(json_path: Path, db: Session) -> int:
    """
    Load results from a JSON file.

    Args:
        json_path: Path to JSON file
        db: Database session

    Returns:
        Number of race results loaded
    """
    logger.info(f"Loading results from {json_path.name}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meet_id = data['meet_id']
    races_data = data.get('races', [])
    loaded_count = 0

    for race_data in races_data:
        try:
            race_number = race_data['race_key']['race_number']

            # Find the race in database (from entries)
            race = db.query(Race).join(Race.meet).filter(
                Race.meet.has(meet_id=meet_id),
                Race.race_number == int(race_number)
            ).first()

            if not race:
                logger.warning(f"Race {meet_id}-R{race_number} not found in database, skipping")
                continue

            # Check if results already exist
            existing_result = db.query(RaceResult).filter(
                RaceResult.race_id == race.id
            ).first()

            if existing_result:
                logger.debug(f"Results for race {race.id} already exist, skipping")
                continue

            # Create race result
            fractional_times = None
            winning_time_seconds = None

            if race_data.get('fraction'):
                fractional_times = race_data['fraction']
                if fractional_times.get('winning_time'):
                    # Try to get total seconds
                    winning_time_seconds = fractional_times['winning_time'].get('total_seconds')

            race_result = RaceResult(
                race_id=race.id,
                fractional_times=fractional_times,
                winning_time_seconds=winning_time_seconds,
                also_ran=race_data.get('also_ran')
            )

            db.add(race_result)
            db.flush()  # Get race_result ID

            # Mark race as finished
            race.has_finished = True
            race.has_results = True

            # Load runner results
            finish_position = 1
            runners_data = race_data.get('runners', [])

            for runner_data in runners_data:
                try:
                    # Find the runner by program number
                    runner = db.query(Runner).filter(
                        Runner.race_id == race.id,
                        Runner.program_number == runner_data['program_number']
                    ).first()

                    if not runner:
                        logger.warning(
                            f"Runner #{runner_data['program_number']} "
                            f"({runner_data.get('horse_name')}) not found in race {race.id}"
                        )
                        finish_position += 1
                        continue

                    # Create runner result
                    runner_result = RunnerResult(
                        runner_id=runner.id,
                        race_result_id=race_result.id,
                        finish_position=finish_position,
                        win_payoff=runner_data.get('win_payoff'),
                        place_payoff=runner_data.get('place_payoff'),
                        show_payoff=runner_data.get('show_payoff')
                    )

                    db.add(runner_result)
                    finish_position += 1

                except Exception as e:
                    logger.error(f"Error loading runner result: {e}")
                    continue

            # Load payoffs
            payoffs_data = race_data.get('payoffs', [])
            for payoff_data in payoffs_data:
                try:
                    payoff = Payoff(
                        race_id=race.id,
                        wager_type=payoff_data.get('wager_type'),
                        wager_name=payoff_data.get('wager_name'),
                        winning_numbers=payoff_data.get('winning_numbers'),
                        base_amount=payoff_data.get('base_amount'),
                        payoff_amount=payoff_data.get('payoff_amount'),
                        total_pool=payoff_data.get('total_pool'),
                        number_of_winning_tickets=payoff_data.get('number_of_rights'),
                        carryover=payoff_data.get('carryover')
                    )

                    db.add(payoff)

                except Exception as e:
                    logger.error(f"Error loading payoff: {e}")
                    continue

            loaded_count += 1

        except Exception as e:
            logger.error(f"Error loading race result: {e}")
            continue

    db.flush()
    logger.info(f"Loaded {loaded_count} new race results")
    return loaded_count


def load_all_results() -> int:
    """
    Load all results JSON files from data/raw directory.

    Returns:
        Total number of race results loaded
    """
    logger.info("Starting results data load")

    # Find all results JSON files
    results_files = list(settings.raw_data_dir.glob("results_*.json"))

    if not results_files:
        logger.warning("No results JSON files found")
        return 0

    logger.info(f"Found {len(results_files)} results files")

    total_loaded = 0

    with get_db_context() as db:
        for json_file in results_files:
            try:
                count = load_results_from_json(json_file, db)
                total_loaded += count
            except Exception as e:
                logger.error(f"Error processing {json_file.name}: {e}")
                continue

    logger.info(f"✓ Total race results loaded: {total_loaded}")
    return total_loaded


if __name__ == "__main__":
    from src.utils.logger import setup_logging

    setup_logging("load_results")

    total = load_all_results()
    print(f"\n✓ Loaded {total} race results into database")