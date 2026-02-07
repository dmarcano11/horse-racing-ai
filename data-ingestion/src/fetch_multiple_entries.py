"""Fetch entries for multiple meets."""
import sys
from pathlib import Path
from datetime import date
import argparse
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def fetch_all_entries_for_date(target_date: date, max_meets: int = None):
    """
    Fetch entries for all meets on a specific date.

    Args:
        target_date: Date to fetch entries for
        max_meets: Maximum number of meets to fetch (None = all)
    """
    logger = setup_logging("fetch_entries")
    client = RacingAPIClient()

    try:
        # Get meets
        logger.info(f"Fetching meets for {target_date}")
        meets = client.get_meets(start_date=target_date)

        if not meets.meets:
            logger.warning(f"No meets found for {target_date}")
            return

        logger.info(f"Found {meets.total_meets} meets")

        # Limit if specified
        meets_to_fetch = meets.meets[:max_meets] if max_meets else meets.meets

        logger.info(f"Fetching entries for {len(meets_to_fetch)} meets")

        # Fetch entries for each meet
        for i, meet in enumerate(meets_to_fetch, 1):
            logger.info(f"\n[{i}/{len(meets_to_fetch)}] {meet.track_name}")

            # Rate limit pause
            if i > 1:
                time.sleep(1)

            try:
                entries = client.get_entries(meet.meet_id)

                logger.info(
                    f"  ✓ {entries.total_races} races, "
                    f"{entries.total_runners} runners"
                )

                # Save to file
                filepath = client.save_entries_to_file(entries)
                logger.info(f"  Saved: {filepath.name}")

            except Exception as e:
                logger.error(f"  ✗ Failed to fetch {meet.track_name}: {e}")
                continue

        logger.info("\n" + "=" * 60)
        logger.info("✓ Completed fetching entries")
        logger.info("=" * 60)

    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch race entries for multiple meets")
    parser.add_argument(
        "--date",
        type=str,
        help="Date (YYYY-MM-DD). Defaults to today"
    )
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of meets to fetch (default: all)"
    )

    args = parser.parse_args()

    # Parse date
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    # Fetch entries
    fetch_all_entries_for_date(target_date, args.max)


if __name__ == "__main__":
    main()