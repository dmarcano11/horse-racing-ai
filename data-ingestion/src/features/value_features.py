"""Value feature calculator (odds-based)."""
from typing import Dict, Optional
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import Runner, Race, Meet, RunnerResult
from src.features.base import FeatureCalculator


class ValueFeatureCalculator(FeatureCalculator):
    """Calculate value features based on odds."""

    def calculate_value_features(
            self,
            runner: Runner,
            race: Race
    ) -> Dict[str, float]:
        """
        Calculate value features.

        Args:
            runner: Runner object
            race: Race object

        Returns:
            Dictionary of features
        """
        features = {}

        # Morning line odds
        ml_odds = runner.morning_line_decimal or 0.0
        features['ml_odds_decimal'] = ml_odds
        features['ml_odds_prob'] = self.normalize_odds(ml_odds)

        # Odds rank in field (1 = favorite, 2 = second choice, etc.)
        features['ml_odds_rank'] = self._get_odds_rank(runner, race)

        # Is favorite
        features['is_favorite'] = 1.0 if features['ml_odds_rank'] == 1 else 0.0

        # Odds category (longshot, overlay, etc.)
        features.update(self._categorize_odds(ml_odds))

        return features

    def _get_odds_rank(
            self,
            runner: Runner,
            race: Race
    ) -> int:
        """
        Get the odds rank of this runner in the field.

        Args:
            runner: Runner object
            race: Race object

        Returns:
            Rank (1 = favorite)
        """
        # Get all active runners with odds
        runners = self.db.query(Runner).filter(
            Runner.race_id == race.id,
            Runner.is_scratched == False,
            Runner.morning_line_decimal.isnot(None)
        ).order_by(Runner.morning_line_decimal.asc()).all()

        # Find rank
        for rank, r in enumerate(runners, 1):
            if r.id == runner.id:
                return rank

        return 99  # Unknown

    def _categorize_odds(
            self,
            odds_decimal: float
    ) -> Dict[str, float]:
        """
        Categorize odds into buckets.

        Args:
            odds_decimal: Decimal odds

        Returns:
            One-hot encoded odds categories
        """
        features = {}

        # Convert to traditional odds range
        if odds_decimal <= 0:
            category = 'unknown'
        elif odds_decimal < 1.0:  # Less than even money (< 1/1)
            category = 'heavy_favorite'
        elif odds_decimal < 3.0:  # 1/1 to 3/1
            category = 'favorite'
        elif odds_decimal < 5.0:  # 3/1 to 5/1
            category = 'second_tier'
        elif odds_decimal < 10.0:  # 5/1 to 10/1
            category = 'mid_price'
        elif odds_decimal < 20.0:  # 10/1 to 20/1
            category = 'longshot'
        else:  # 20/1+
            category = 'extreme_longshot'

        # One-hot encode
        categories = [
            'heavy_favorite', 'favorite', 'second_tier',
            'mid_price', 'longshot', 'extreme_longshot', 'unknown'
        ]

        for cat in categories:
            features[f'odds_category_{cat}'] = 1.0 if cat == category else 0.0

        return features