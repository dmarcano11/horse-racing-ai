"""Jockey feature calculator."""
from typing import Dict, Optional
from datetime import date, timedelta
from sqlalchemy import func, and_, Integer, case
from sqlalchemy.orm import Session

from src.db.models import (
    Jockey, Runner, Race, Meet, RaceResult, RunnerResult, Track
)
from src.features.base import FeatureCalculator


class JockeyFeatureCalculator(FeatureCalculator):
    """Calculate jockey-related features."""

    def calculate_jockey_features(
        self,
        jockey_id: int,
        race_date: date,
        track_id: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate all jockey features as of a specific date.

        IMPORTANT: Only uses data BEFORE race_date to prevent data leakage.

        Args:
            jockey_id: Jockey ID
            race_date: Date of the race (features calculated before this)
            track_id: Optional track ID for track-specific stats

        Returns:
            Dictionary of features
        """
        features = {}

        # Overall statistics (lifetime before this race)
        overall_stats = self._get_overall_stats(jockey_id, race_date)
        features['jockey_win_rate'] = overall_stats['win_rate']
        features['jockey_total_races'] = overall_stats['total_races']
        features['jockey_roi'] = overall_stats['roi']

        # Track-specific statistics
        if track_id:
            track_stats = self._get_track_stats(jockey_id, race_date, track_id)
            features['jockey_track_win_rate'] = track_stats['win_rate']
            features['jockey_track_races'] = track_stats['total_races']
        else:
            features['jockey_track_win_rate'] = features['jockey_win_rate']
            features['jockey_track_races'] = 0

        # Recent form (last 7, 30, 90 days)
        features.update(self._get_recent_form(jockey_id, race_date))

        return features

    def _get_overall_stats(
        self,
        jockey_id: int,
        before_date: date
    ) -> Dict[str, float]:
        """
        Get overall jockey statistics before a date.

        Args:
            jockey_id: Jockey ID
            before_date: Only include races before this date

        Returns:
            Statistics dictionary
        """
        # Query all races this jockey rode before the target date
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
            Runner.jockey_id == jockey_id,
            Meet.date < before_date,
            RunnerResult.finish_position.isnot(None)
        ).first()

        total_races = results.total or 0
        wins = results.wins or 0
        total_returned = float(results.total_returned or 0)

        # Assume $2 base bet per race
        total_wagered = total_races * 2.0

        return {
            'win_rate': self.calculate_win_rate(wins, total_races),
            'total_races': total_races,
            'roi': self.calculate_roi(total_wagered, total_returned)
        }

    def _get_track_stats(
        self,
        jockey_id: int,
        before_date: date,
        track_id: int
    ) -> Dict[str, float]:
        """
        Get jockey statistics at specific track.

        Args:
            jockey_id: Jockey ID
            before_date: Only include races before this date
            track_id: Track ID

        Returns:
            Statistics dictionary
        """
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
            Runner.jockey_id == jockey_id,
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
        jockey_id: int,
        before_date: date
    ) -> Dict[str, float]:
        """
        Get jockey recent form statistics.

        Args:
            jockey_id: Jockey ID
            before_date: Calculate form before this date

        Returns:
            Form statistics for different time windows
        """
        features = {}

        # Calculate for 7, 30, 90 day windows
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
                Runner.jockey_id == jockey_id,
                Meet.date >= start_date,
                Meet.date < before_date,
                RunnerResult.finish_position.isnot(None)
            ).first()

            total_races = results.total or 0
            wins = results.wins or 0

            features[f'jockey_win_rate_{days}d'] = self.calculate_win_rate(wins, total_races)
            features[f'jockey_races_{days}d'] = total_races

        return features