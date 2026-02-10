"""Debug feature building."""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.db.models import Race, Meet, Runner, RunnerResult


def debug_feature_building():
    """Debug why features aren't being built."""

    with get_db_context() as db:
        target_date = date(2026, 2, 7)

        print("\n" + "=" * 60)
        print(f"DEBUGGING DATE: {target_date}")
        print("=" * 60)

        # Step 1: Check races
        races = db.query(Race, Meet).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Meet.date == target_date,
            Race.has_results == True
        ).all()

        print(f"\n1. Races with results: {len(races)}")

        if not races:
            print("   ❌ No races found!")
            return

        # Step 2: Check first race
        race, meet = races[0]
        print(f"\n2. First race details:")
        print(f"   Race ID: {race.id}")
        print(f"   Race Number: {race.race_number}")
        print(f"   Meet: {meet.track.track_name}")
        print(f"   Has Results: {race.has_results}")

        # Step 3: Check runners
        all_runners = db.query(Runner).filter(
            Runner.race_id == race.id
        ).all()

        print(f"\n3. All runners in race: {len(all_runners)}")

        # Step 4: Check active (non-scratched) runners
        active_runners = db.query(Runner).filter(
            Runner.race_id == race.id,
            Runner.is_scratched == False
        ).all()

        print(f"   Active runners (not scratched): {len(active_runners)}")

        if not active_runners:
            print("   ❌ All runners are scratched!")

            # Check scratch status
            for runner in all_runners:
                print(f"      Runner {runner.id}: is_scratched={runner.is_scratched}")
        else:
            print(f"   ✓ Found {len(active_runners)} active runners")

            # Check results for active runners
            runner = active_runners[0]
            print(f"\n4. First active runner:")
            print(f"   Runner ID: {runner.id}")
            print(f"   Horse: {runner.horse.name}")
            print(f"   Jockey ID: {runner.jockey_id}")
            print(f"   Trainer ID: {runner.trainer_id}")

            # Check if result exists
            result = db.query(RunnerResult).filter(
                RunnerResult.runner_id == runner.id
            ).first()

            if result:
                print(f"   ✓ Has result: Position {result.finish_position}")
            else:
                print(f"   ❌ No result found!")

        # Step 5: Check across all races
        print(f"\n5. Checking all {len(races)} races...")

        total_runners = 0
        total_active = 0
        races_with_active = 0

        for race, meet in races:
            active = db.query(Runner).filter(
                Runner.race_id == race.id,
                Runner.is_scratched == False
            ).count()

            total_active += active

            all_count = db.query(Runner).filter(
                Runner.race_id == race.id
            ).count()

            total_runners += all_count

            if active > 0:
                races_with_active += 1

        print(f"   Total runners: {total_runners}")
        print(f"   Active runners: {total_active}")
        print(f"   Races with active runners: {races_with_active}/{len(races)}")

        if total_active == 0:
            print("\n❌ PROBLEM: All runners are scratched!")
            print("   This might be a data loading issue.")
        else:
            print(f"\n✓ Should be able to build features for {total_active} runners")


if __name__ == "__main__":
    debug_feature_building()