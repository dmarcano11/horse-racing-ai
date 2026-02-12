"""Performance metrics for backtesting."""
import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Calculate comprehensive backtesting performance metrics."""

    def calculate_metrics(
            self,
            results_df: pd.DataFrame,
            initial_bankroll: float = 1000.0,
            strategy_name: str = "Strategy"
    ) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics.

        Args:
            results_df: DataFrame from backtester
            initial_bankroll: Starting bankroll
            strategy_name: Name of strategy

        Returns:
            Dictionary of metrics
        """
        if results_df.empty:
            logger.warning("No results to analyze")
            return {}

        metrics = {}

        # Basic stats
        metrics['total_bets'] = len(results_df)
        metrics['total_wagered'] = results_df['bet_amount'].sum()
        metrics['total_profit'] = results_df['profit'].sum()
        metrics['total_returned'] = results_df['return_amount'].sum()

        # Win stats
        wins = results_df[results_df['actual_win'] == 1]
        metrics['winning_bets'] = len(wins)
        metrics['losing_bets'] = len(results_df) - len(wins)
        metrics['win_rate'] = len(wins) / len(results_df) * 100

        # ROI
        metrics['roi'] = (metrics['total_profit'] / metrics['total_wagered'] * 100)

        # Bankroll
        metrics['final_bankroll'] = initial_bankroll + metrics['total_profit']
        metrics['bankroll_growth'] = (
                (metrics['final_bankroll'] - initial_bankroll) / initial_bankroll * 100
        )

        # Average metrics
        metrics['avg_bet'] = results_df['bet_amount'].mean()
        metrics['avg_odds'] = results_df['odds_decimal'].mean()
        metrics['avg_win_probability'] = results_df['win_probability'].mean()

        # Risk metrics
        metrics['max_drawdown'] = self._calculate_max_drawdown(results_df)
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(results_df)
        metrics['profit_factor'] = self._calculate_profit_factor(results_df)

        # Streak analysis
        metrics['max_win_streak'] = self._calculate_max_streak(results_df, win=True)
        metrics['max_loss_streak'] = self._calculate_max_streak(results_df, win=False)

        self._print_metrics(metrics, strategy_name)

        return metrics

    def _calculate_max_drawdown(self, results_df: pd.DataFrame) -> float:
        """
        Calculate maximum drawdown.

        Max drawdown = largest peak-to-trough decline in bankroll.
        Lower is better.
        """
        bankroll = results_df['bankroll'].values

        peak = bankroll[0]
        max_drawdown = 0.0

        for value in bankroll:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def _calculate_sharpe_ratio(
            self,
            results_df: pd.DataFrame,
            risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted returns).

        Higher is better. > 1.0 is good, > 2.0 is excellent.
        """
        profits = results_df['profit'].values

        if len(profits) < 2:
            return 0.0

        mean_return = np.mean(profits)
        std_return = np.std(profits)

        if std_return == 0:
            return 0.0

        # Annualized (assuming ~10 bets per day)
        sharpe = (mean_return / std_return) * np.sqrt(252 * 10)

        return sharpe

    def _calculate_profit_factor(self, results_df: pd.DataFrame) -> float:
        """
        Calculate profit factor.

        Profit factor = gross profit / gross loss.
        > 1.0 means profitable. > 1.5 is good.
        """
        gross_profit = results_df[results_df['profit'] > 0]['profit'].sum()
        gross_loss = abs(results_df[results_df['profit'] < 0]['profit'].sum())

        if gross_loss == 0:
            return float('inf')

        return gross_profit / gross_loss

    def _calculate_max_streak(
            self,
            results_df: pd.DataFrame,
            win: bool = True
    ) -> int:
        """Calculate maximum winning or losing streak."""
        streak = 0
        max_streak = 0

        for actual_win in results_df['actual_win']:
            if (win and actual_win == 1) or (not win and actual_win == 0):
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0

        return max_streak

    def _print_metrics(self, metrics: Dict[str, float], strategy_name: str):
        """Print formatted metrics."""
        print(f"\n{'=' * 80}")
        print(f"PERFORMANCE METRICS: {strategy_name}")
        print(f"{'=' * 80}")

        print(f"\n📊 BETTING SUMMARY:")
        print(f"  Total bets:        {metrics['total_bets']:.0f}")
        print(f"  Winning bets:      {metrics['winning_bets']:.0f} ({metrics['win_rate']:.1f}%)")
        print(f"  Losing bets:       {metrics['losing_bets']:.0f}")
        print(f"  Average bet:       ${metrics['avg_bet']:.2f}")
        print(f"  Average odds:      {metrics['avg_odds']:.2f}")

        print(f"\n💰 FINANCIAL RESULTS:")
        print(f"  Total wagered:     ${metrics['total_wagered']:.2f}")
        print(f"  Total returned:    ${metrics['total_returned']:.2f}")
        print(f"  Total profit:      ${metrics['total_profit']:+.2f}")
        print(f"  ROI:               {metrics['roi']:+.2f}%")
        print(f"  Final bankroll:    ${metrics['final_bankroll']:.2f}")
        print(f"  Bankroll growth:   {metrics['bankroll_growth']:+.2f}%")

        print(f"\n📉 RISK METRICS:")
        print(f"  Max drawdown:      {metrics['max_drawdown']:.2f}%")
        print(f"  Sharpe ratio:      {metrics['sharpe_ratio']:.3f}")
        print(f"  Profit factor:     {metrics['profit_factor']:.3f}")
        print(f"  Max win streak:    {metrics['max_win_streak']:.0f}")
        print(f"  Max loss streak:   {metrics['max_loss_streak']:.0f}")

        # Summary rating
        print(f"\n🎯 SUMMARY:")
        if metrics['roi'] > 5:
            print(f"  ✅ PROFITABLE strategy! ROI: {metrics['roi']:+.2f}%")
        elif metrics['roi'] > 0:
            print(f"  ⚠️  Marginally profitable. ROI: {metrics['roi']:+.2f}%")
        else:
            print(f"  ❌ Unprofitable. ROI: {metrics['roi']:+.2f}%")

        if metrics['sharpe_ratio'] > 1.0:
            print(f"  ✅ Good risk-adjusted returns (Sharpe: {metrics['sharpe_ratio']:.2f})")

        print(f"{'=' * 80}\n")

    def compare_strategies(
            self,
            strategy_results: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Compare multiple strategies.

        Args:
            strategy_results: {strategy_name: metrics_dict}

        Returns:
            Comparison DataFrame
        """
        key_metrics = [
            'total_bets', 'win_rate', 'total_wagered',
            'total_profit', 'roi', 'final_bankroll',
            'max_drawdown', 'sharpe_ratio', 'profit_factor'
        ]

        comparison = {}
        for strategy_name, metrics in strategy_results.items():
            comparison[strategy_name] = {
                k: metrics.get(k, 0) for k in key_metrics
            }

        df = pd.DataFrame(comparison).T
        df = df.sort_values('roi', ascending=False)

        print("\n" + "=" * 80)
        print("STRATEGY COMPARISON (sorted by ROI)")
        print("=" * 80)
        print(df.to_string())
        print("=" * 80)

        return df