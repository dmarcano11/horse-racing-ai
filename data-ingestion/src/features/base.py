"""Base feature calculator."""
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from decimal import Decimal

from src.db.models import (
    Race, Runner, Horse, Jockey, Trainer,
    RaceResult, RunnerResult, Meet
)


class FeatureCalculator:
    """Base class for feature calculation."""

    def __init__(self, db: Session):
        """
        Initialize feature calculator.

        Args:
            db: Database session
        """
        self.db = db

    def calculate_win_rate(
            self,
            wins: int,
            total_races: int,
            smoothing: int = 10
    ) -> float:
        """
        Calculate win rate with Laplace smoothing.

        Args:
            wins: Number of wins
            total_races: Total races
            smoothing: Smoothing parameter (pseudo-counts)

        Returns:
            Win rate (0-1)
        """
        if total_races == 0:
            return 0.1  # Prior estimate

        # Laplace smoothing: (wins + 1) / (total + smoothing)
        return (wins + 1) / (total_races + smoothing)

    def calculate_roi(
            self,
            total_wagered: float,
            total_returned: float
    ) -> float:
        """
        Calculate ROI.

        Args:
            total_wagered: Total amount wagered
            total_returned: Total amount returned

        Returns:
            ROI as decimal (0.5 = 50% return)
        """
        if total_wagered == 0:
            return 0.0

        return (total_returned - total_wagered) / total_wagered

    def days_between(
            self,
            date1: date,
            date2: date
    ) -> int:
        """
        Calculate days between two dates.

        Args:
            date1: First date
            date2: Second date

        Returns:
            Number of days
        """
        return abs((date2 - date1).days)

    def normalize_odds(
            self,
            odds_decimal: Optional[float]
    ) -> float:
        """
        Normalize odds to implied probability.

        Args:
            odds_decimal: Decimal odds (e.g., 5.0 for 5/1)

        Returns:
            Implied probability (0-1)
        """
        if not odds_decimal or odds_decimal <= 0:
            return 0.05  # Default very low probability

        # Convert to probability: 1 / (odds + 1)
        # Example: 5.0 odds → 1/6 = 0.167 (16.7%)
        return 1.0 / (odds_decimal + 1.0)