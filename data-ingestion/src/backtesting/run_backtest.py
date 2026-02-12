"""Run complete backtesting pipeline."""
from pathlib import Path
import pandas as pd

from src.backtesting.backtester import Backtester
from src.backtesting.betting_strategies import (
    FlatBettingStrategy,
    KellyCriterionStrategy,
    ValueBettingStrategy,
    ConfidenceBettingStrategy
)
from src.backtesting.performance_metrics import PerformanceAnalyzer
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def run_complete_backtest():
    """Run backtest with all strategies."""
    setup_logging("backtest")

    print("\n" + "=" * 80)
    print("🏇 HORSE RACING AI - BACKTESTING ENGINE")
    print("=" * 80)

    # Paths
    model_path = Path("models/tuned/random_forest_tuned.pkl")
    data_path = Path("data/processed/features_complete.csv")

    # Check files exist
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return

    if not data_path.exists():
        print(f"❌ Data not found: {data_path}")
        return

    # Define strategies to test
    strategies = [
        FlatBettingStrategy(bet_amount=2.0, bankroll=1000.0),
        KellyCriterionStrategy(fraction=0.25, bankroll=1000.0),
        ValueBettingStrategy(min_edge=0.05, bet_amount=2.0, bankroll=1000.0),
        ConfidenceBettingStrategy(min_probability=0.30, bankroll=1000.0)
    ]

    # Run backtest for each strategy
    analyzer = PerformanceAnalyzer()
    all_results = {}
    all_metrics = {}

    for strategy in strategies:
        print(f"\n{'=' * 80}")
        print(f"📊 Testing: {strategy.name}")
        print(f"{'=' * 80}")

        backtester = Backtester(
            model_path=model_path,
            data_path=data_path,
            strategy=strategy,
            min_odds=1.0,
            max_odds=50.0
        )

        # Run simulation
        results_df = backtester.run()

        if results_df.empty:
            print(f"⚠️  No bets placed for {strategy.name}")
            continue

        # Calculate metrics
        metrics = analyzer.calculate_metrics(
            results_df,
            initial_bankroll=strategy.initial_bankroll,
            strategy_name=strategy.name
        )

        all_results[strategy.name] = results_df
        all_metrics[strategy.name] = metrics

        # Save individual results
        output_dir = Path("data/backtesting")
        output_dir.mkdir(exist_ok=True, parents=True)

        safe_name = strategy.name.lower().replace(' ', '_')
        results_df.to_csv(
            output_dir / f"backtest_{safe_name}.csv",
            index=False
        )

    # Compare all strategies
    if len(all_metrics) > 1:
        comparison_df = analyzer.compare_strategies(all_metrics)
        comparison_df.to_csv(
            "data/backtesting/strategy_comparison.csv"
        )

        # Print best strategy
        best_strategy = comparison_df.index[0]
        best_roi = comparison_df.loc[best_strategy, 'roi']

        print(f"\n{'=' * 80}")
        print(f"🏆 BEST STRATEGY: {best_strategy}")
        print(f"   ROI: {best_roi:+.2f}%")
        print(f"{'=' * 80}")

    print("\n✓ Backtest complete!")
    print(f"  Results saved to: data/backtesting/")

    return all_results, all_metrics


if __name__ == "__main__":
    run_complete_backtest()