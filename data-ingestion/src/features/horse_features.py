"""Horse feature calculator."""
from typing import Dict, Optional
from datetime import date
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from src.db.models import (
    Horse, Runner, Race, Meet, RaceResult, RunnerResult
)
from src.features.base import FeatureCalculator


class HorseFeatureCalculator(FeatureCalculator):
    """Calculate horse-related features."""

    def calculate_horse_features(
        self,
        horse_id: int,
        race_date: date
    ) -> Dict[str, float]:
        """
        Calculate all horse features as of a specific date.

        Args:
            horse_id: Horse ID
            race_date: Date of the race

        Returns:
            Dictionary of features
        """
        features = {}

        # Overall statistics
        overall_stats = self._get_overall_stats(horse_id, race_date)
        features['horse_win_rate'] = overall_stats['win_rate']
        features['horse_total_races'] = overall_stats['total_races']
        features['horse_avg_finish'] = overall_stats['avg_finish']

        # Days since last race
        features['horse_days_since_last_race'] = self._get_days_since_last_race(
            horse_id, race_date
        )

        # Career earnings (if available)
        features['horse_career_earnings'] = overall_stats['earnings']

        return features

    def _get_overall_stats(
        self,
        horse_id: int,
        before_date: date
    ) -> Dict[str, float]:
        """Get overall horse statistics."""
        results = self.db.query(
            func.count(RunnerResult.id).label('total'),
            func.sum(
                case((RunnerResult.finish_position == 1, 1), else_=0)
            ).label('wins'),
            func.avg(RunnerResult.finish_position).label('avg_finish'),
            func.sum(RunnerResult.win_payoff).label('earnings')
        ).join(
            Runner, RunnerResult.runner_id == Runner.id
        ).join(
            Race, Runner.race_id == Race.id
        ).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Runner.horse_id == horse_id,
            Meet.date < before_date,
            RunnerResult.finish_position.isnot(None)
        ).first()

        total_races = results.total or 0
        wins = results.wins or 0
        avg_finish = float(results.avg_finish or 5.0)
        earnings = float(results.earnings or 0)

        return {
            'win_rate': self.calculate_win_rate(wins, total_races),
            'total_races': total_races,
            'avg_finish': avg_finish,
            'earnings': earnings
        }

    def _get_days_since_last_race(
        self,
        horse_id: int,
        current_date: date
    ) -> int:
        """
        Calculate days since horse's last race.

        Args:
            horse_id: Horse ID
            current_date: Current race date

        Returns:
            Days since last race (999 if no previous races)
        """
        last_race = self.db.query(Meet.date).join(
            Race, Race.meet_id == Meet.id
        ).join(
            Runner, Runner.race_id == Race.id
        ).filter(
            Runner.horse_id == horse_id,
            Meet.date < current_date
        ).order_by(Meet.date.desc()).first()

        if not last_race:
            return 999  # First race

        return self.days_between(last_race.date, current_date)