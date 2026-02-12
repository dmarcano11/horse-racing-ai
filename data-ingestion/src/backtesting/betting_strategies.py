"""Betting strategies for backtesting."""
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BettingStrategy(ABC):
    """Base class for all betting strategies."""

    def __init__(self, name: str, bankroll: float = 1000.0):
        """
        Initialize strategy.

        Args:
            name: Strategy name
            bankroll: Starting bankroll in dollars
        """
        self.name = name
        self.initial_bankroll = bankroll
        self.bankroll = bankroll

    @abstractmethod
    def calculate_bet(
            self,
            win_probability: float,
            odds_decimal: float,
            **kwargs
    ) -> float:
        """
        Calculate bet amount.

        Args:
            win_probability: Model's predicted win probability
            odds_decimal: Decimal odds (e.g., 3.0 = 3-1)

        Returns:
            Bet amount in dollars (0 = no bet)
        """
        pass

    def reset(self):
        """Reset bankroll to initial amount."""
        self.bankroll = self.initial_bankroll

    def can_bet(self, amount: float) -> bool:
        """Check if bankroll can cover bet."""
        return self.bankroll >= amount and amount > 0

    def __repr__(self):
        return f"{self.name} (bankroll: ${self.bankroll:.2f})"


class FlatBettingStrategy(BettingStrategy):
    """
    Flat betting - bet same amount every race.

    Simple but effective baseline strategy.
    Good for comparing models on equal footing.
    """

    def __init__(self, bet_amount: float = 2.0, bankroll: float = 1000.0):
        """
        Initialize flat betting.

        Args:
            bet_amount: Fixed bet amount per race
            bankroll: Starting bankroll
        """
        super().__init__("Flat Betting", bankroll)
        self.bet_amount = bet_amount

    def calculate_bet(
            self,
            win_probability: float,
            odds_decimal: float,
            **kwargs
    ) -> float:
        """Always bet fixed amount."""
        return self.bet_amount if self.can_bet(self.bet_amount) else 0.0


class KellyCriterionStrategy(BettingStrategy):
    """
    Kelly Criterion - mathematically optimal bet sizing.

    Formula: f = (bp - q) / b
    Where:
        f = fraction of bankroll to bet
        b = decimal odds - 1 (net odds)
        p = probability of winning
        q = probability of losing (1 - p)

    Maximizes long-term bankroll growth.
    """

    def __init__(
            self,
            fraction: float = 0.25,
            min_bet: float = 2.0,
            max_bet_fraction: float = 0.10,
            bankroll: float = 1000.0
    ):
        """
        Initialize Kelly Criterion.

        Args:
            fraction: Kelly fraction (0.25 = quarter Kelly, safer)
            min_bet: Minimum bet amount
            max_bet_fraction: Maximum bet as fraction of bankroll
            bankroll: Starting bankroll
        """
        super().__init__("Kelly Criterion", bankroll)
        self.fraction = fraction  # Use fractional Kelly for safety
        self.min_bet = min_bet
        self.max_bet_fraction = max_bet_fraction

    def calculate_bet(
            self,
            win_probability: float,
            odds_decimal: float,
            **kwargs
    ) -> float:
        """Calculate Kelly optimal bet."""
        if odds_decimal <= 1.0:
            return 0.0

        b = odds_decimal - 1
        p = win_probability
        q = 1 - p

        kelly = (b * p - q) / b

        # Only bet when positive expected value
        if kelly <= 0:
            return 0.0

        # Cap Kelly fraction to prevent overflow
        kelly = min(kelly, 0.25)  # Never bet more than 25% of bankroll

        # Apply fractional Kelly
        fractional_kelly = kelly * self.fraction

        # Calculate bet amount from CURRENT bankroll
        bet_amount = self.bankroll * fractional_kelly

        # Hard limits
        bet_amount = max(bet_amount, self.min_bet)
        max_bet = min(self.bankroll * self.max_bet_fraction, 50.0)  # Hard cap at $50
        bet_amount = min(bet_amount, max_bet)

        return bet_amount if self.can_bet(bet_amount) else 0.0


class ValueBettingStrategy(BettingStrategy):
    """
    Value betting - only bet when model finds value.

    Bets when model probability > implied odds probability.
    Example: Model says 40% chance, odds imply 25% → value bet!

    This is the most sophisticated strategy and most used
    by professional bettors.
    """

    def __init__(
            self,
            min_edge: float = 0.05,
            bet_amount: float = 2.0,
            bankroll: float = 1000.0
    ):
        """
        Initialize value betting.

        Args:
            min_edge: Minimum edge required to bet (0.05 = 5%)
            bet_amount: Base bet amount
            bankroll: Starting bankroll
        """
        super().__init__("Value Betting", bankroll)
        self.min_edge = min_edge
        self.bet_amount = bet_amount

    def calculate_bet(
            self,
            win_probability: float,
            odds_decimal: float,
            **kwargs
    ) -> float:
        """
        Bet only when model finds value.

        Args:
            win_probability: Model predicted probability
            odds_decimal: Decimal odds

        Returns:
            Bet amount (0 if no value found)
        """
        if odds_decimal <= 1.0:
            return 0.0

        # Implied probability from odds
        implied_probability = 1.0 / (odds_decimal + 1.0)

        # Edge = model probability - implied probability
        edge = win_probability - implied_probability

        # Only bet when edge exceeds minimum
        if edge < self.min_edge:
            return 0.0

        return self.bet_amount if self.can_bet(self.bet_amount) else 0.0


class ConfidenceBettingStrategy(BettingStrategy):
    """
    Confidence-based betting - bet more on high confidence predictions.

    Scales bet size based on model's predicted probability.
    Higher probability = larger bet.
    """

    def __init__(
            self,
            min_probability: float = 0.30,
            base_bet: float = 2.0,
            max_bet: float = 20.0,
            bankroll: float = 1000.0
    ):
        """
        Initialize confidence betting.

        Args:
            min_probability: Minimum probability to bet
            base_bet: Minimum bet amount
            max_bet: Maximum bet amount
            bankroll: Starting bankroll
        """
        super().__init__("Confidence Betting", bankroll)
        self.min_probability = min_probability
        self.base_bet = base_bet
        self.max_bet = max_bet

    def calculate_bet(
            self,
            win_probability: float,
            odds_decimal: float,
            **kwargs
    ) -> float:
        """
        Scale bet with confidence level.

        Args:
            win_probability: Model predicted probability
            odds_decimal: Decimal odds

        Returns:
            Scaled bet amount
        """
        # Only bet above minimum threshold
        if win_probability < self.min_probability:
            return 0.0

        # Scale bet linearly from base to max
        # 30% prob → base_bet, 60%+ prob → max_bet
        scale = (win_probability - self.min_probability) / (0.60 - self.min_probability)
        scale = min(scale, 1.0)  # Cap at 1.0

        bet_amount = self.base_bet + scale * (self.max_bet - self.base_bet)

        return bet_amount if self.can_bet(bet_amount) else 0.0

"""
IMPROVEMENT                    FILE TO EDIT                    DIFFICULTY
─────────────────────────────────────────────────────────────────────────
Add new features               src/features/*_features.py      Easy ⭐
Fix model calibration          src/ml/baseline_model.py        Easy ⭐
Add speed figures              src/features/horse_features.py  Medium ⭐⭐
Try new ML models              src/ml/new_model.py             Easy ⭐
Tune betting thresholds        src/backtesting/betting_*.py    Easy ⭐
Add more training data         fetch_multiple_results.py       Easy ⭐
Try neural networks            src/ml/neural_net.py            Hard ⭐⭐⭐
"""