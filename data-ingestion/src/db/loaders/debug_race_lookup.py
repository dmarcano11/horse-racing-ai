"""Debug why results loader can't find races."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.db.models import Race, Meet
from src.config import settings


def debug_race_lookup():
    """Debug race lookup issue."""

    # Get first results file
    results_files = list(settings.raw_data_dir.glob("results_*.json"))

    if not results_files:
        print("No results files found!")
        return

    results_file = results_files[0]

    with open(results_file) as f:
        data = json.load(f)

    meet_id_from_file = data['meet_id']

    print("\n" + "=" * 60)
    print(f"RESULTS FILE: {results_file.name}")
    print("=" * 60)
    print(f"\nMeet ID from file: {meet_id_from_file}")

    # Get first race
    if data.get('races'):
        race_data = data['races'][0]
        race_number = race_data.get('race_number')
        print(f"First race number: {race_number}")
        print(f"Looking for: {meet_id_from_file}-R{race_number}")

    # Check database
    with get_db_context() as db:
        print("\n" + "=" * 60)
        print("DATABASE CHECK")
        print("=" * 60)

        # Check if meet exists
        meet = db.query(Meet).filter(Meet.meet_id == meet_id_from_file).first()

        if meet:
            print(f"\n✓ Meet found in database!")
            print(f"  DB Meet ID: {meet.id}")
            print(f"  Meet external ID: {meet.meet_id}")
            print(f"  Track: {meet.track.track_name}")
            print(f"  Date: {meet.date}")

            # Check races for this meet
            races = db.query(Race).filter(Race.meet_id == meet.id).all()
            print(f"\n  Races for this meet: {len(races)}")

            if races:
                print(f"  First race number: {races[0].race_number}")
                print(f"  Race IDs: {[r.id for r in races[:5]]}")
            else:
                print("  ❌ NO RACES found for this meet!")
        else:
            print(f"\n❌ Meet {meet_id_from_file} NOT found in database!")

            # Show what meets we DO have
            all_meets = db.query(Meet.meet_id).limit(10).all()
            print(f"\n  Sample of meets in database:")
            for m_id, in all_meets:
                print(f"    {m_id}")


if __name__ == "__main__":
    debug_race_lookup()