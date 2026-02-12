"""Core backtesting engine."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import joblib
import logging

from src.backtesting.betting_strategies import BettingStrategy
from src.ml.data_preparation import DataPreparation
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class BetResult:
    """Result of a single bet."""

    def __init__(
        self,
        race_id: float,
        runner_id: float,
        bet_amount: float,
        win_probability: float,
        odds_decimal: float,
        actual_win: int,
        win_payoff: float = 0.0
    ):
        self.race_id = race_id
        self.runner_id = runner_id
        self.bet_amount = bet_amount
        self.win_probability = win_probability
        self.odds_decimal = odds_decimal
        self.actual_win = actual_win
        self.win_payoff = win_payoff

        # Calculate return
        if actual_win == 1 and win_payoff > 0:
            self.return_amount = (bet_amount / 2.0) * win_payoff
        elif actual_win == 1 and win_payoff == 0:
            self.return_amount = bet_amount * (odds_decimal + 1.0)
        else:
            self.return_amount = 0.0

        self.profit = self.return_amount - self.bet_amount

    def to_dict(self) -> dict:
        return {
            'race_id': self.race_id,
            'runner_id': self.runner_id,
            'bet_amount': self.bet_amount,
            'win_probability': self.win_probability,
            'odds_decimal': self.odds_decimal,
            'actual_win': self.actual_win,
            'win_payoff': self.win_payoff,
            'return_amount': self.return_amount,
            'profit': self.profit
        }


class Backtester:
    """
    Core backtesting engine.

    IMPORTANT: Only tests on held-out data the model has never seen.
    Uses same 80/20 time-based split as model training.
    """

    def __init__(
        self,
        model_path: Path,
        data_path: Path,
        strategy: BettingStrategy,
        train_ratio: float = 0.8,
        min_odds: float = 1.0,
        max_odds: float = 50.0
    ):
        self.strategy = strategy
        self.min_odds = min_odds
        self.max_odds = max_odds
        self.train_ratio = train_ratio

        # Load model
        logger.info(f"Loading model from {model_path}")
        self.model = joblib.load(model_path)

        # Load and prepare data - USE SAME SPLIT AS TRAINING
        logger.info(f"Loading data from {data_path}")
        self.data_prep = DataPreparation()

        raw_df = self.data_prep.load_data(data_path)
        complete_df = self.data_prep.filter_complete_data(raw_df)
        complete_df = self.data_prep.handle_missing_values(complete_df)

        self.feature_columns = self.data_prep.get_feature_columns(complete_df)

        # Apply SAME time-based split as training
        # Train on first 80%, test on last 20%
        train_df, test_df = self.data_prep.time_based_split(
            complete_df, train_ratio=train_ratio
        )

        # Fit scaler on TRAIN only, transform TEST only
        X_train = train_df[self.feature_columns]
        X_test = test_df[self.feature_columns]

        self.scaler = StandardScaler()
        self.scaler.fit(X_train)  # Fit on train only!

        # Backtest only on TEST set (model has never seen this)
        self.test_df = test_df.copy()
        self.X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=self.feature_columns,
            index=test_df.index
        )

        logger.info(f"Train samples: {len(train_df)} (model trained on these)")
        logger.info(f"Test samples: {len(test_df)} (backtesting on these only)")
        logger.info(f"  Test wins: {(test_df['target_win'] == 1).sum()}")
        logger.info(f"  Test losses: {(test_df['target_win'] == 0).sum()}")

    def get_win_probabilities(self) -> np.ndarray:
        """Get win probabilities using properly scaled test data."""
        return self.model.predict_proba(self.X_test_scaled)[:, 1]

    def run(self) -> pd.DataFrame:
        """Run backtest simulation on test set only."""
        logger.info(f"\nRunning backtest with {self.strategy.name}")

        self.strategy.reset()

        # Get predictions on test set
        win_probabilities = self.get_win_probabilities()
        self.test_df = self.test_df.copy()
        self.test_df['win_probability'] = win_probabilities

        bet_results = []
        bankroll_history = [self.strategy.bankroll]

        # Group by race
        races = self.test_df.groupby('race_id')

        for race_id, race_df in races:
            race_probs = race_df['win_probability'].values
            race_odds = race_df['ml_odds_decimal'].values
            race_wins = race_df['target_win'].values
            race_runner_ids = race_df['runner_id'].values

            for idx in range(len(race_df)):
                odds = race_odds[idx]
                win_prob = race_probs[idx]
                actual_win = race_wins[idx]
                runner_id = race_runner_ids[idx]

                # Skip missing or out-of-range odds
                if odds <= self.min_odds or odds > self.max_odds or odds == 0:
                    continue

                # Calculate bet
                bet_amount = self.strategy.calculate_bet(
                    win_probability=float(win_prob),
                    odds_decimal=float(odds)
                )

                if bet_amount <= 0:
                    continue

                win_payoff = race_df.iloc[idx].get('win_payoff', 0.0) or 0.0

                result = BetResult(
                    race_id=race_id,
                    runner_id=runner_id,
                    bet_amount=bet_amount,
                    win_probability=float(win_prob),
                    odds_decimal=float(odds),
                    actual_win=int(actual_win),
                    win_payoff=float(win_payoff)
                )

                self.strategy.bankroll += result.profit
                bet_results.append(result.to_dict())
                bankroll_history.append(self.strategy.bankroll)

        if not bet_results:
            logger.warning("No bets placed!")
            return pd.DataFrame()

        results_df = pd.DataFrame(bet_results)
        results_df['bankroll'] = bankroll_history[1:len(results_df) + 1]
        results_df['cumulative_profit'] = results_df['profit'].cumsum()
        results_df['cumulative_bets'] = results_df['bet_amount'].cumsum()
        results_df['running_roi'] = (
            results_df['cumulative_profit'] / results_df['cumulative_bets'] * 100
        )

        logger.info(f"✓ Placed {len(results_df)} bets")
        logger.info(f"  Final bankroll: ${self.strategy.bankroll:.2f}")
        logger.info(f"  Total profit: ${results_df['profit'].sum():.2f}")

        return results_df