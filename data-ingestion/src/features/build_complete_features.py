"""Build complete feature matrix with all available data."""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import get_db_context
from src.features.feature_builder import FeatureBuilder
from src.utils.logger import setup_logging


def build_complete_features():
    """Build features for all dates with results."""
    setup_logging("build_features")

    print("\n" + "=" * 80)
    print("BUILDING COMPLETE FEATURE MATRIX")
    print("=" * 80)

    with get_db_context() as db:
        builder = FeatureBuilder(db)

        # Build features for Feb 1-7, 2026
        # Using broad date range to capture all available data
        df = builder.build_features_for_date_range(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 7),
            only_with_results=True
        )

        print(f"\n✓ Built features for {len(df)} runners")

        # Filter to only complete data (with results)
        df_complete = df[df['target_win'] >= 0]

        print(f"✓ Runners with results: {len(df_complete)}")
        print(f"  Wins: {(df_complete['target_win'] == 1).sum()}")
        print(f"  Losses: {(df_complete['target_win'] == 0).sum()}")

        # Save
        output_path = Path("data/processed/features_complete.csv")
        df.to_csv(output_path, index=False)

        print(f"\n✓ Saved complete feature matrix to: {output_path}")
        print("=" * 80)

        return df


if __name__ == "__main__":
    build_complete_features()