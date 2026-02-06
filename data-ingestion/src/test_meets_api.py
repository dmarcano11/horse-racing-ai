"""Test script for Racing API meets endpoint."""
from datetime import date, timedelta
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def main():
    """Test the Racing API meets endpoint."""

    # Set up logging
    logger = setup_logging("test_meets_api", level=10)  # DEBUG level

    logger.info("=" * 60)
    logger.info("Testing Racing API - Meets Endpoint")
    logger.info("=" * 60)

    # Initialize client
    client = RacingAPIClient()

    try:
        # Test 1: Get today's meets
        logger.info("\n--- Test 1: Today's Meets ---")
        today = date.today()
        meets_today = client.get_meets(start_date=today)

        logger.info(f"Total meets today: {meets_today.total_meets}")
        logger.info(f"Tracks: {', '.join(meets_today.get_tracks())}")

        # Display first few meets
        for i, meet in enumerate(meets_today.meets[:5], 1):
            logger.info(f"{i}. {meet.track_name} ({meet.track_id}) - {meet.date}")

        # Save to file
        filepath = client.save_meets_to_file(meets_today)
        logger.info(f"Saved to: {filepath}")

        # Wait between tests to avoid rate limiting
        logger.info("\n⏳ Waiting 2 seconds before next test...")
        time.sleep(2)

        # Test 2: Get next 7 days of meets
        logger.info("\n--- Test 2: Next 7 Days ---")
        end_date = today + timedelta(days=7)
        meets_week = client.get_meets(start_date=today, end_date=end_date)

        logger.info(f"Total meets in next 7 days: {meets_week.total_meets}")
        logger.info(f"Unique tracks: {len(meets_week.get_tracks())}")

        # Count meets by date
        from collections import Counter
        dates = [meet.date for meet in meets_week.meets]
        date_counts = Counter(dates)

        logger.info("\nMeets per day:")
        for date_str, count in sorted(date_counts.items()):
            logger.info(f"  {date_str}: {count} meets")

        # Save to file
        filepath = client.save_meets_to_file(meets_week)
        logger.info(f"Saved to: {filepath}")

        # Test 3: Filter by specific track
        logger.info("\n--- Test 3: Filter by Track ---")

        # Find any track that has multiple meets
        track_counts = Counter(meet.track_name for meet in meets_week.meets)
        popular_tracks = [track for track, count in track_counts.items() if count > 1]

        if popular_tracks:
            test_track = popular_tracks[0]
            track_meets = meets_week.filter_by_track(test_track)
            logger.info(f"Found {len(track_meets)} {test_track} meets:")
            for meet in track_meets:
                logger.info(f"  - {meet.date} (Meet ID: {meet.meet_id})")
        else:
            logger.info("No tracks with multiple meets found")

        # Test 4: Pagination test (SKIP if we don't have enough data)
        if meets_week.total_meets >= 50:
            logger.info("\n⏳ Waiting 3 seconds before pagination test...")
            time.sleep(3)

            logger.info("\n--- Test 4: Pagination ---")
            meets_page2 = client.get_meets(
                start_date=today,
                end_date=end_date,
                skip=50
            )
            logger.info(f"Page 2 has {meets_page2.total_meets} meets")
        else:
            logger.info("\n--- Test 4: Pagination ---")
            logger.info("Skipping pagination test (not enough data)")

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