"""Trainer feature calculator."""
from typing import Dict, Optional
from datetime import date, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from src.db.models import (
    Trainer, Runner, Race, Meet, RaceResult, RunnerResult
)
from src.features.base import FeatureCalculator


class TrainerFeatureCalculator(FeatureCalculator):
    """Calculate trainer-related features."""

    def calculate_trainer_features(
        self,
        trainer_id: int,
        race_date: date,
        track_id: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate all trainer features as of a specific date.

        Args:
            trainer_id: Trainer ID
            race_date: Date of the race
            track_id: Optional track ID

        Returns:
            Dictionary of features
        """
        features = {}

        # Overall statistics
        overall_stats = self._get_overall_stats(trainer_id, race_date)
        features['trainer_win_rate'] = overall_stats['win_rate']
        features['trainer_total_races'] = overall_stats['total_races']
        features['trainer_roi'] = overall_stats['roi']

        # Track-specific statistics
        if track_id:
            track_stats = self._get_track_stats(trainer_id, race_date, track_id)
            features['trainer_track_win_rate'] = track_stats['win_rate']
            features['trainer_track_races'] = track_stats['total_races']
        else:
            features['trainer_track_win_rate'] = features['trainer_win_rate']
            features['trainer_track_races'] = 0

        # Recent form
        features.update(self._get_recent_form(trainer_id, race_date))

        return features

    def _get_overall_stats(
        self,
        trainer_id: int,
        before_date: date
    ) -> Dict[str, float]:
        """Get overall trainer statistics."""
        results = self.db.query(
            func.count(RunnerResult.id).label('total'),
            func.sum(
                case((RunnerResult.finish_position == 1, 1), else_=0)
            ).label('wins'),
            func.sum(RunnerResult.win_payoff).label('total_returned')
        ).join(
            Runner, RunnerResult.runner_id == Runner.id
        ).join(
            Race, Runner.race_id == Race.id
        ).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Runner.trainer_id == trainer_id,
            Meet.date < before_date,
            RunnerResult.finish_position.isnot(None)
        ).first()

        total_races = results.total or 0
        wins = results.wins or 0
        total_returned = float(results.total_returned or 0)
        total_wagered = total_races * 2.0

        return {
            'win_rate': self.calculate_win_rate(wins, total_races),
            'total_races': total_races,
            'roi': self.calculate_roi(total_wagered, total_returned)
        }

    def _get_track_stats(
        self,
        trainer_id: int,
        before_date: date,
        track_id: int
    ) -> Dict[str, float]:
        """Get trainer statistics at specific track."""
        results = self.db.query(
            func.count(RunnerResult.id).label('total'),
            func.sum(
                case((RunnerResult.finish_position == 1, 1), else_=0)
            ).label('wins')
        ).join(
            Runner, RunnerResult.runner_id == Runner.id
        ).join(
            Race, Runner.race_id == Race.id
        ).join(
            Meet, Race.meet_id == Meet.id
        ).filter(
            Runner.trainer_id == trainer_id,
            Meet.track_id == track_id,
            Meet.date < before_date,
            RunnerResult.finish_position.isnot(None)
        ).first()

        total_races = results.total or 0
        wins = results.wins or 0

        return {
            'win_rate': self.calculate_win_rate(wins, total_races),
            'total_races': total_races
        }

    def _get_recent_form(
        self,
        trainer_id: int,
        before_date: date
    ) -> Dict[str, float]:
        """Get trainer recent form."""
        features = {}

        for days in [7, 30, 90]:
            start_date = before_date - timedelta(days=days)

            results = self.db.query(
                func.count(RunnerResult.id).label('total'),
                func.sum(
                    case((RunnerResult.finish_position == 1, 1), else_=0)
                ).label('wins')
            ).join(
                Runner, RunnerResult.runner_id == Runner.id
            ).join(
                Race, Runner.race_id == Race.id
            ).join(
                Meet, Race.meet_id == Meet.id
            ).filter(
                Runner.trainer_id == trainer_id,
                Meet.date >= start_date,
                Meet.date < before_date,
                RunnerResult.finish_position.isnot(None)
            ).first()

            total_races = results.total or 0
            wins = results.wins or 0

            features[f'trainer_win_rate_{days}d'] = self.calculate_win_rate(wins, total_races)
            features[f'trainer_races_{days}d'] = total_races

        return features