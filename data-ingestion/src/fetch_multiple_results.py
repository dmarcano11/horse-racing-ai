"""Fetch results for multiple meets."""
import sys
from pathlib import Path
from datetime import date, timedelta
import argparse
import time
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.racing_api_client import RacingAPIClient
from src.utils.logger import setup_logging


def fetch_all_results_for_date(target_date: date, max_meets: int = None):
    """
    Fetch results for all meets on a specific date.

    Args:
        target_date: Date to fetch results for
        max_meets: Maximum number of meets to fetch (None = all)
    """
    logger = setup_logging("fetch_results")
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

        logger.info(f"Fetching results for {len(meets_to_fetch)} meets")

        # Fetch results for each meet
        successful = 0
        not_found = 0
        failed = 0

        for i, meet in enumerate(meets_to_fetch, 1):
            logger.info(f"\n[{i}/{len(meets_to_fetch)}] {meet.track_name}")

            # Rate limit pause
            if i > 1:
                time.sleep(1)

            try:
                results = client.get_results(meet.meet_id)

                logger.info(
                    f"  ✓ {results.total_races} races, "
                    f"{results.completed_races} with results"
                )

                # Save to file
                filepath = client.save_results_to_file(results)
                logger.info(f"  Saved: {filepath.name}")

                successful += 1

            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 404:
                    # 404 is expected - results not available
                    logger.warning(f"  ⚠ Results not available (may not be published yet)")
                    not_found += 1
                else:
                    # Other HTTP errors
                    logger.error(f"  ✗ HTTP Error: {e}")
                    failed += 1
                continue
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                failed += 1
                continue

        logger.info("\n" + "=" * 60)
        logger.info(f"Results Summary:")
        logger.info(f"  ✓ Successfully fetched: {successful}/{len(meets_to_fetch)}")
        if not_found > 0:
            logger.info(f"  ⚠ Results not available: {not_found}")
        if failed > 0:
            logger.info(f"  ✗ Failed with errors: {failed}")
        logger.info("=" * 60)

    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch race results for multiple meets")
    parser.add_argument(
        "--date",
        type=str,
        help="Date (YYYY-MM-DD). Defaults to yesterday"
    )
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of meets to fetch (default: all)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=1,
        help="Days back from today (default: 1 for yesterday)"
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        target_date = date.today() - timedelta(days=args.days_back)

    # Fetch results
    fetch_all_results_for_date(target_date, args.max)


if __name__ == "__main__":
    main()