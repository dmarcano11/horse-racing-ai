"""Test the complete feature builder."""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.features.feature_builder import FeatureBuilder
from src.db.models import Race, Meet, RunnerResult, RaceResult


def test_feature_builder():
    """Test building complete feature matrix."""

    with get_db_context() as db:
        # First, find dates that have results
        print("\n" + "=" * 60)
        print("FINDING DATES WITH RESULTS")
        print("=" * 60)

        dates_with_results = db.query(Meet.date).join(
            Race, Race.meet_id == Meet.id
        ).filter(
            Race.has_results == True
        ).distinct().order_by(Meet.date.desc()).limit(5).all()

        if not dates_with_results:
            print("\n❌ No dates with results found!")
            print("Please run the results loader first:")
            print("  python -m src.db.loaders.load_results")
            return

        print("\nDates with results:")
        for d, in dates_with_results:
            race_count = db.query(Race).join(Meet).filter(
                Meet.date == d,
                Race.has_results == True
            ).count()
            print(f"  {d}: {race_count} races")

        # Find a date that has ACTUAL runner results
        for d, in dates_with_results:
            runner_count = db.query(RunnerResult).join(
                RaceResult
            ).join(
                Race
            ).join(
                Meet
            ).filter(
                Meet.date == d
            ).count()

            if runner_count > 0:
                target_date = d
                print(f"Found {runner_count} runner results for {d}")
                break
        else:
            print("No dates with runner results found!")
            return

        print("\n" + "=" * 60)
        print("BUILDING FEATURE MATRIX")
        print("=" * 60)

        print(f"\nUsing date: {target_date}")
        print("Building features (only races with results)...")

        builder = FeatureBuilder(db)

        df = builder.build_features_for_date_range(
            target_date,
            target_date,
            only_with_results=True
        )

        if len(df) == 0:
            print("\n❌ No features built! This shouldn't happen.")
            print("Check that races have results loaded.")
            return

        print(f"\n✓ Built features for {len(df)} runners")
        print(f"✓ Total features: {len(df.columns)}")

        # Show feature columns
        print("\n--- FEATURE COLUMNS ---")
        feature_cols = sorted([col for col in df.columns if col not in ['runner_id', 'race_id', 'meet_id']])
        for i, col in enumerate(feature_cols, 1):
            print(f"{i:3d}. {col}")

        # Show statistics
        print("\n--- TARGET VARIABLE DISTRIBUTION ---")

        # Filter out rows without results (target_win = -1)
        df_with_results = df[df['target_win'] >= 0]

        if len(df_with_results) > 0:
            wins = int((df_with_results['target_win'] == 1.0).sum())
            losses = int((df_with_results['target_win'] == 0.0).sum())
            total = wins + losses

            if total > 0:
                print(f"Total runners with results: {len(df_with_results)}")
                print(f"Wins: {wins} ({wins / total * 100:.1f}%)")
                print(f"Losses: {losses} ({losses / total * 100:.1f}%)")
            else:
                print("No finished races found")
        else:
            print("No runners with results found")

        # Show runners without results
        no_results = len(df[df['target_win'] < 0])
        if no_results > 0:
            print(f"Runners without results yet: {no_results}")

        # Show sample rows
        print("\n--- SAMPLE DATA (First 5 Runners) ---")
        sample_cols = [
            'runner_id', 'race_id',
            'jockey_win_rate', 'trainer_win_rate', 'horse_win_rate',
            'ml_odds_decimal', 'is_favorite',
            'field_size', 'post_position',
            'target_win'
        ]

        available_cols = [col for col in sample_cols if col in df.columns]
        print(df[available_cols].head(5).to_string(index=False))

        # Show feature statistics
        print("\n--- FEATURE STATISTICS ---")

        # Numeric columns only (exclude identifiers and target)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        exclude_cols = ['runner_id', 'race_id', 'meet_id', 'target_win', 'target_finish_position']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]

        stats = df[feature_cols].describe().loc[['mean', 'std', 'min', 'max']]
        print(stats.iloc[:, :10].to_string())  # Show first 10 features

        # Save to CSV
        output_file = Path("data/processed/features_sample.csv")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)

        print(f"\n✓ Saved features to: {output_file}")
        print("=" * 60)


if __name__ == "__main__":
    test_feature_builder()