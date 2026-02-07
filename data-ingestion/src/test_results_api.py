"""Test script for Racing API results endpoint."""
from datetime import date, timedelta
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def main():
    """Test the Racing API results endpoint."""

    logger = setup_logging("test_results_api", level=10)

    logger.info("=" * 60)
    logger.info("Testing Racing API - Results Endpoint")
    logger.info("=" * 60)

    client = RacingAPIClient()

    try:
        # Step 1: Get yesterday's meets (more likely to have results)
        logger.info("\n--- Step 1: Get Yesterday's Meets ---")
        yesterday = date.today() - timedelta(days=1)
        meets = client.get_meets(start_date=yesterday)

        if not meets.meets:
            logger.warning("No meets found for yesterday!")
            # Try 2 days ago
            yesterday = date.today() - timedelta(days=2)
            meets = client.get_meets(start_date=yesterday)

        logger.info(f"Found {meets.total_meets} meets on {yesterday}")

        # Step 2: Get results for first meet
        logger.info("\n--- Step 2: Get Results for First Meet ---")
        first_meet = meets.meets[0]
        logger.info(f"Getting results for: {first_meet.track_name} (ID: {first_meet.meet_id})")

        time.sleep(1)  # Rate limit pause

        results = client.get_results(first_meet.meet_id)

        logger.info(f"Track: {results.track_name}")
        logger.info(f"Date: {results.date}")
        logger.info(f"Total Races: {results.total_races}")
        logger.info(f"Completed Races: {results.completed_races}")

        # Step 3: Analyze first completed race
        completed_races = [r for r in results.races if r.runners]

        if completed_races:
            logger.info("\n--- Step 3: First Completed Race ---")
            race = completed_races[0]

            logger.info(f"Race {race.race_number}: {race.race_name or 'N/A'}")
            logger.info(f"Distance: {race.distance_value} {race.distance_unit}")
            logger.info(f"Surface: {race.surface_description}")
            logger.info(f"Track Condition: {race.track_condition_description}")

            # Winner info
            if race.winner:
                logger.info(f"\n🏆 Winner: #{race.winner.program_number} {race.winner.horse_name}")
                logger.info(f"   Jockey: {race.winner.jockey_name}")
                logger.info(f"   Trainer: {race.winner.trainer_name}")
                logger.info(
                    f"   Win Payoff: ${race.winner.win_payoff:.2f}" if race.winner.win_payoff else "   Win Payoff: N/A")

            # Fractional times
            if race.fraction and race.fraction.has_fractions:
                logger.info(f"\n⏱️  Times:")
                fractions = race.fraction.get_all_fractions()
                for i, frac in enumerate(fractions, 1):
                    if frac and frac.total_seconds:
                        logger.info(f"   Fraction {i}: {frac}")

                if race.fraction.winning_time:
                    logger.info(f"   Final Time: {race.fraction.winning_time}")

            # Top finishers
            logger.info(f"\n📊 Top Finishers:")
            for i, runner in enumerate(race.runners[:5], 1):
                payoff_str = f"${runner.win_payoff:.2f}" if runner.win_payoff else "N/A"
                logger.info(
                    f"   {i}. #{runner.program_number} {runner.horse_name} - "
                    f"J: {runner.jockey_name}, Win: {payoff_str}"
                )

            # Payoffs
            if race.payoffs:
                logger.info(f"\n💰 Payoffs ({len(race.payoffs)} total):")

                # Win/Place/Show
                for wager_type in ['WN', 'PL', 'SH']:
                    payoff = race.get_payoff_by_type(wager_type)
                    if payoff:
                        logger.info(
                            f"   {payoff.wager_name}: #{payoff.winning_numbers} "
                            f"= ${payoff.payoff_amount:.2f}"
                        )

                # Exotics
                exotics = race.get_exotic_payoffs()
                if exotics:
                    logger.info(f"\n   Exotic Payoffs:")
                    for payoff in exotics[:5]:  # First 5 exotics
                        logger.info(
                            f"   {payoff.wager_name}: {payoff.winning_numbers} "
                            f"= ${payoff.payoff_amount:.2f} "
                            f"(ROI: {payoff.roi_percentage:.1f}%)" if payoff.roi_percentage else ""
                        )

        # Step 4: Summary statistics
        logger.info("\n--- Step 4: Summary Statistics ---")

        total_payoffs = sum(len(r.payoffs or []) for r in completed_races)
        logger.info(f"Total Payoffs Recorded: {total_payoffs}")

        races_with_times = sum(1 for r in completed_races if r.fraction and r.fraction.has_fractions)
        logger.info(f"Races with Fractional Times: {races_with_times}/{len(completed_races)}")

        # Step 5: Save to file
        logger.info("\n--- Step 5: Save Data ---")
        filepath = client.save_results_to_file(results)
        logger.info(f"Saved to: {filepath}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())