"""Fetch historical meets data."""
import sys
from pathlib import Path
from datetime import date, timedelta
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def fetch_meets_for_date_range(start_date: date, end_date: date):
    """
    Fetch meets for a date range.

    Args:
        start_date: Start date
        end_date: End date (inclusive)
    """
    logger = setup_logging("fetch_meets")
    client = RacingAPIClient()

    try:
        logger.info(f"Fetching meets from {start_date} to {end_date}")

        # Fetch meets for the date range
        meets = client.get_meets(start_date=start_date, end_date=end_date)

        logger.info(f"Found {meets.total_meets} meets")

        if meets.total_meets == 0:
            logger.warning("No meets found for this date range")
            return

        # Save to file
        filepath = client.save_meets_to_file(meets)
        logger.info(f"Saved to: {filepath}")

        # Show summary
        tracks = meets.get_tracks()
        logger.info(f"\nTracks ({len(tracks)}):")
        for track in sorted(tracks):
            count = len([m for m in meets.meets if m.track_name == track])
            logger.info(f"  {track}: {count} meets")

        logger.info("\n" + "=" * 60)
        logger.info(f"✓ Successfully fetched {meets.total_meets} meets")
        logger.info("=" * 60)

    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch historical meets data")
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    # Parse dates
    start_date = date.fromisoformat(args.start_date)
    end_date = date.fromisoformat(args.end_date)

    # Validate
    if end_date < start_date:
        print("Error: end-date must be after start-date")
        return 1

    # Fetch meets
    fetch_meets_for_date_range(start_date, end_date)
    return 0


if __name__ == "__main__":
    sys.exit(main())