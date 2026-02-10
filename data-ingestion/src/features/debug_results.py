"""Debug results loading."""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.db.models import Race, Meet, Runner, RunnerResult, RaceResult


def debug_results():
    """Debug why results aren't found."""

    with get_db_context() as db:
        target_date = date(2026, 2, 7)

        print("\n" + "=" * 60)
        print(f"DEBUGGING RESULTS FOR: {target_date}")
        print("=" * 60)

        # Get first race
        race, meet = db.query(Race, Meet).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Meet.date == target_date,
            Race.has_results == True
        ).first()

        print(f"\n1. Race: {meet.track.track_name} - Race {race.race_number}")
        print(f"   Race ID: {race.id}")
        print(f"   Has results flag: {race.has_results}")

        # Check if RaceResult exists
        race_result = db.query(RaceResult).filter(
            RaceResult.race_id == race.id
        ).first()

        if race_result:
            print(f"\n2. ✓ RaceResult exists (ID: {race_result.id})")
        else:
            print(f"\n2. ❌ NO RaceResult found for this race!")
            print("   This is why target_win is -1")
            return

        # Check runners
        runners = db.query(Runner).filter(
            Runner.race_id == race.id,
            Runner.is_scratched == False
        ).all()

        print(f"\n3. Active runners: {len(runners)}")

        # Check first runner
        runner = runners[0]
        print(f"\n4. First runner:")
        print(f"   Runner ID: {runner.id}")
        print(f"   Horse: {runner.horse.name}")
        print(f"   Program number: {runner.program_number}")
        print(f"   Morning line odds: {runner.morning_line_odds}")
        print(f"   Morning line decimal: {runner.morning_line_decimal}")

        # Check if RunnerResult exists
        runner_result = db.query(RunnerResult).filter(
            RunnerResult.runner_id == runner.id
        ).first()

        if runner_result:
            print(f"\n5. ✓ RunnerResult exists:")
            print(f"   Finish position: {runner_result.finish_position}")
            print(f"   Win payoff: {runner_result.win_payoff}")
        else:
            print(f"\n5. ❌ NO RunnerResult found!")

        # Check all runners for this race
        print(f"\n6. Checking all {len(runners)} runners...")

        results_count = db.query(RunnerResult).join(
            Runner
        ).filter(
            Runner.race_id == race.id
        ).count()

        print(f"   RunnerResults found: {results_count}/{len(runners)}")

        if results_count == 0:
            print("\n❌ PROBLEM: No RunnerResults loaded for any runner!")
            print("   Need to check results loader.")


if __name__ == "__main__":
    debug_results()