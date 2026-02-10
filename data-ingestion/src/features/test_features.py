"""Test feature calculators."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.db.models import Runner, Race, Meet
from src.features.jockey_features import JockeyFeatureCalculator
from src.features.trainer_features import TrainerFeatureCalculator
from src.features.horse_features import HorseFeatureCalculator


def test_feature_calculators():
    """Test all feature calculators."""

    with get_db_context() as db:
        # Get a sample runner
        runner = db.query(Runner).join(
            Race
        ).join(
            Meet
        ).filter(
            Runner.jockey_id.isnot(None),
            Runner.trainer_id.isnot(None)
        ).first()

        if not runner:
            print("No runners found!")
            return

        race = runner.race
        meet = race.meet
        race_date = meet.date

        print("\n" + "=" * 60)
        print("FEATURE CALCULATOR TEST")
        print("=" * 60)
        print(f"\nRace: {meet.track.track_name} - {race_date} - Race {race.race_number}")
        print(f"Horse: {runner.horse.name}")
        print(f"Jockey: {runner.jockey.first_name} {runner.jockey.last_name}" if runner.jockey else "No jockey")
        print(f"Trainer: {runner.trainer.first_name} {runner.trainer.last_name}" if runner.trainer else "No trainer")

        # Calculate jockey features
        if runner.jockey_id:
            print("\n--- JOCKEY FEATURES ---")
            jockey_calc = JockeyFeatureCalculator(db)
            jockey_features = jockey_calc.calculate_jockey_features(
                runner.jockey_id,
                race_date,
                meet.track_id
            )

            for key, value in sorted(jockey_features.items()):
                print(f"  {key}: {value:.4f}")

        # Calculate trainer features
        if runner.trainer_id:
            print("\n--- TRAINER FEATURES ---")
            trainer_calc = TrainerFeatureCalculator(db)
            trainer_features = trainer_calc.calculate_trainer_features(
                runner.trainer_id,
                race_date,
                meet.track_id
            )

            for key, value in sorted(trainer_features.items()):
                print(f"  {key}: {value:.4f}")

        # Calculate horse features
        print("\n--- HORSE FEATURES ---")
        horse_calc = HorseFeatureCalculator(db)
        horse_features = horse_calc.calculate_horse_features(
            runner.horse_id,
            race_date
        )

        for key, value in sorted(horse_features.items()):
            print(f"  {key}: {value:.4f}")

        print("\n" + "=" * 60)
        print("✓ Feature calculation complete!")
        print("=" * 60)


if __name__ == "__main__":
    test_feature_calculators()