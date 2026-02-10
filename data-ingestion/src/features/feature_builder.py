"""Master feature builder - combines all feature calculators."""
from typing import Dict, List, Optional
from datetime import date
import pandas as pd
from sqlalchemy.orm import Session

from src.db.models import Runner, Race, Meet, Track, RaceResult, RunnerResult
from src.features.jockey_features import JockeyFeatureCalculator
from src.features.trainer_features import TrainerFeatureCalculator
from src.features.horse_features import HorseFeatureCalculator
from src.features.race_features import RaceFeatureCalculator
from src.features.value_features import ValueFeatureCalculator


class FeatureBuilder:
    """Build complete feature matrix for ML."""

    def __init__(self, db: Session):
        """
        Initialize feature builder.

        Args:
            db: Database session
        """
        self.db = db

        # Initialize feature calculators
        self.jockey_calc = JockeyFeatureCalculator(db)
        self.trainer_calc = TrainerFeatureCalculator(db)
        self.horse_calc = HorseFeatureCalculator(db)
        self.race_calc = RaceFeatureCalculator(db)
        self.value_calc = ValueFeatureCalculator(db)

    def build_features_for_runner(
            self,
            runner: Runner,
            race: Race,
            meet: Meet
    ) -> Dict[str, float]:
        """
        Build complete feature set for a single runner.

        Args:
            runner: Runner object
            race: Race object
            meet: Meet object

        Returns:
            Dictionary of all features
        """
        features = {}

        # Basic identifiers (not features, but useful for tracking)
        features['runner_id'] = float(runner.id)
        features['race_id'] = float(race.id)
        features['meet_id'] = float(meet.id)

        # Jockey features
        if runner.jockey_id:
            jockey_features = self.jockey_calc.calculate_jockey_features(
                runner.jockey_id,
                meet.date,
                meet.track_id
            )
            features.update(jockey_features)
        else:
            # Fill with defaults if no jockey
            features.update(self._get_default_jockey_features())

        # Trainer features
        if runner.trainer_id:
            trainer_features = self.trainer_calc.calculate_trainer_features(
                runner.trainer_id,
                meet.date,
                meet.track_id
            )
            features.update(trainer_features)
        else:
            # Fill with defaults if no trainer
            features.update(self._get_default_trainer_features())

        # Horse features
        horse_features = self.horse_calc.calculate_horse_features(
            runner.horse_id,
            meet.date
        )
        features.update(horse_features)

        # Race context features
        race_features = self.race_calc.calculate_race_features(race, runner)
        features.update(race_features)

        # Value features (odds)
        value_features = self.value_calc.calculate_value_features(runner, race)
        features.update(value_features)

        # Target variable (if available)
        features['target_win'] = self._get_target_win(runner)
        features['target_finish_position'] = self._get_target_finish_position(runner)

        return features

    def build_features_for_race(
            self,
            race: Race,
            meet: Meet
    ) -> pd.DataFrame:
        """
        Build features for all runners in a race.

        Args:
            race: Race object
            meet: Meet object

        Returns:
            DataFrame with one row per runner
        """
        runners = self.db.query(Runner).filter(
            Runner.race_id == race.id,
            Runner.is_scratched == False
        ).all()

        features_list = []

        for runner in runners:
            features = self.build_features_for_runner(runner, race, meet)
            features_list.append(features)

        return pd.DataFrame(features_list)

    def build_features_for_date_range(
            self,
            start_date: date,
            end_date: date,
            only_with_results: bool = True
    ) -> pd.DataFrame:
        """
        Build features for all races in a date range.

        Args:
            start_date: Start date
            end_date: End date (inclusive)
            only_with_results: Only include races with results

        Returns:
            DataFrame with all features
        """
        # Query races in date range
        query = self.db.query(Race, Meet).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Meet.date >= start_date,
            Meet.date <= end_date
        )

        if only_with_results:
            query = query.filter(Race.has_results == True)

        races_and_meets = query.all()

        all_features = []

        for race, meet in races_and_meets:
            race_features = self.build_features_for_race(race, meet)
            all_features.append(race_features)

        if not all_features:
            return pd.DataFrame()

        return pd.concat(all_features, ignore_index=True)

    def _get_target_win(self, runner: Runner) -> float:
        """
        Get target variable: did this horse win?

        Args:
            runner: Runner object

        Returns:
            1.0 if won, 0.0 if lost, -1.0 if no result
        """
        result = self.db.query(RunnerResult).filter(
            RunnerResult.runner_id == runner.id
        ).first()

        if not result or result.finish_position is None:
            return -1.0  # No result available

        return 1.0 if result.finish_position == 1 else 0.0

    def _get_target_finish_position(self, runner: Runner) -> float:
        """
        Get target variable: finish position.

        Args:
            runner: Runner object

        Returns:
            Finish position or -1.0 if no result
        """
        result = self.db.query(RunnerResult).filter(
            RunnerResult.runner_id == runner.id
        ).first()

        if not result or result.finish_position is None:
            return -1.0

        return float(result.finish_position)

    def _get_default_jockey_features(self) -> Dict[str, float]:
        """Get default jockey features when jockey is unknown."""
        return {
            'jockey_win_rate': 0.1,
            'jockey_total_races': 0.0,
            'jockey_roi': 0.0,
            'jockey_track_win_rate': 0.1,
            'jockey_track_races': 0.0,
            'jockey_win_rate_7d': 0.1,
            'jockey_races_7d': 0.0,
            'jockey_win_rate_30d': 0.1,
            'jockey_races_30d': 0.0,
            'jockey_win_rate_90d': 0.1,
            'jockey_races_90d': 0.0,
        }

    def _get_default_trainer_features(self) -> Dict[str, float]:
        """Get default trainer features when trainer is unknown."""
        return {
            'trainer_win_rate': 0.1,
            'trainer_total_races': 0.0,
            'trainer_roi': 0.0,
            'trainer_track_win_rate': 0.1,
            'trainer_track_races': 0.0,
            'trainer_win_rate_7d': 0.1,
            'trainer_races_7d': 0.0,
            'trainer_win_rate_30d': 0.1,
            'trainer_races_30d': 0.0,
            'trainer_win_rate_90d': 0.1,
            'trainer_races_90d': 0.0,
        }