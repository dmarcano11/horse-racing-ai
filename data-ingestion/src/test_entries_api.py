"""Test script for Racing API entries endpoint."""
from datetime import date
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def main():
    """Test the Racing API entries endpoint."""

    logger = setup_logging("test_entries_api", level=10)

    logger.info("=" * 60)
    logger.info("Testing Racing API - Entries Endpoint")
    logger.info("=" * 60)

    client = RacingAPIClient()

    try:
        # Step 1: Get today's meets
        logger.info("\n--- Step 1: Get Today's Meets ---")
        today = date.today()
        meets = client.get_meets(start_date=today)

        if not meets.meets:
            logger.warning("No meets found for today!")
            return 0

        logger.info(f"Found {meets.total_meets} meets today")

        # Step 2: Get entries for first meet
        logger.info("\n--- Step 2: Get Entries for First Meet ---")
        first_meet = meets.meets[0]
        logger.info(f"Getting entries for: {first_meet.track_name} (ID: {first_meet.meet_id})")

        time.sleep(1)  # Rate limit pause

        entries = client.get_entries(first_meet.meet_id)

        logger.info(f"Track: {entries.track_name}")
        logger.info(f"Date: {entries.date}")
        logger.info(f"Total Races: {entries.total_races}")
        logger.info(f"Total Runners: {entries.total_runners}")

        if entries.weather:
            logger.info(f"Weather: {entries.weather.current_weather_description or 'N/A'}")

        # Step 3: Analyze first race
        if entries.races:
            logger.info("\n--- Step 3: First Race Details ---")
            race = entries.races[0]

            logger.info(f"Race {race.race_number}: {race.race_name or 'N/A'}")
            logger.info(f"Post Time: {race.post_time}")
            logger.info(f"Distance: {race.distance_value} {race.distance_unit}")
            logger.info(f"Surface: {race.surface_description}")
            logger.info(f"Purse: ${race.purse:,}" if race.purse else "Purse: N/A")
            logger.info(f"Total Runners: {race.total_runners}")
            logger.info(f"Active Runners: {race.active_runners}")

            if race.scratched_runners:
                logger.info(f"Scratched: {len(race.scratched_runners)}")
                for runner in race.scratched_runners:
                    logger.info(f"  - #{runner.program_number} {runner.horse_name}")

            # Step 4: Show runners
            logger.info("\n--- Step 4: Runners ---")
            for runner in race.runners[:5]:  # First 5
                if runner.is_scratched:
                    continue

                jockey_name = runner.jockey.display_name if runner.jockey else "Unknown"
                trainer_name = runner.trainer.display_name if runner.trainer else "Unknown"

                logger.info(
                    f"  #{runner.program_number} {runner.horse_name} - "
                    f"J: {jockey_name}, T: {trainer_name}, "
                    f"ML: {runner.morning_line_odds or 'N/A'}"
                )

            # Step 5: Find favorite
            logger.info("\n--- Step 5: Morning Line Favorite ---")
            favorite = race.get_favorite()
            if favorite:
                logger.info(f"Favorite: #{favorite.program_number} {favorite.horse_name}")
                logger.info(f"Odds: {favorite.morning_line_odds}")
                if favorite.jockey:
                    logger.info(f"Jockey: {favorite.jockey.full_name}")
                if favorite.trainer:
                    logger.info(f"Trainer: {favorite.trainer.full_name}")

        # Step 6: Surface breakdown
        logger.info("\n--- Step 6: Races by Surface ---")
        dirt_races = entries.get_races_by_surface("Dirt")
        turf_races = entries.get_races_by_surface("Turf")

        logger.info(f"Dirt Races: {len(dirt_races)}")
        logger.info(f"Turf Races: {len(turf_races)}")

        # Step 7: Save to file
        logger.info("\n--- Step 7: Save Data ---")
        filepath = client.save_entries_to_file(entries)
        logger.info(f"Saved to: {filepath}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests completed successfully!")
        logger.info("=" * 60)

        # Summary
        logger.info("\n--- Summary ---")
        logger.info(f"Meet: {entries.track_name}")
        logger.info(f"Races: {entries.total_races}")
        logger.info(f"Runners: {entries.total_runners}")
        logger.info(f"File: {filepath.name}")

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())