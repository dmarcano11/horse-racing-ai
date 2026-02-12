"""Analyze backtest results to find model edge."""
import pandas as pd
import numpy as np
from pathlib import Path


def analyze_backtest_results():
    """Find where the model performs best."""

    # Load flat betting results (cleanest to analyze)
    results_path = Path("data/backtesting/backtest_flat_betting.csv")

    if not results_path.exists():
        print("No backtest results found!")
        return

    df = pd.read_csv(results_path)

    print("\n" + "=" * 80)
    print("BACKTEST DEEP ANALYSIS")
    print("=" * 80)

    # Overall stats
    total_bets = len(df)
    wins = (df['actual_win'] == 1).sum()
    roi = df['profit'].sum() / df['bet_amount'].sum() * 100

    print(f"\n📊 OVERALL: {total_bets} bets, {wins} wins ({wins / total_bets * 100:.1f}%), ROI: {roi:+.1f}%")

    # Analysis by odds range
    print("\n📊 PERFORMANCE BY ODDS RANGE:")
    print(f"{'Odds Range':20s} {'Bets':>6} {'Wins':>6} {'Win%':>7} {'ROI':>8}")
    print("-" * 55)

    bins = [(1, 3, "Favorite (1-3)"), (3, 6, "2nd tier (3-6)"),
            (6, 10, "Mid (6-10)"), (10, 20, "Longshot (10-20)"),
            (20, 50, "Big shot (20-50)")]

    for low, high, label in bins:
        mask = (df['odds_decimal'] >= low) & (df['odds_decimal'] < high)
        subset = df[mask]
        if len(subset) == 0:
            continue

        subset_wins = (subset['actual_win'] == 1).sum()
        subset_roi = subset['profit'].sum() / subset['bet_amount'].sum() * 100

        print(f"{label:20s} {len(subset):>6} {subset_wins:>6} "
              f"{subset_wins / len(subset) * 100:>6.1f}% {subset_roi:>+7.1f}%")

    # Analysis by win probability bucket
    print("\n📊 PERFORMANCE BY MODEL CONFIDENCE:")
    print(f"{'Probability':20s} {'Bets':>6} {'Wins':>6} {'Win%':>7} {'ROI':>8}")
    print("-" * 55)

    prob_bins = [(0, 0.1, "Very Low (<10%)"), (0.1, 0.2, "Low (10-20%)"),
                 (0.2, 0.3, "Medium (20-30%)"), (0.3, 0.5, "High (30-50%)"),
                 (0.5, 1.0, "Very High (>50%)")]

    for low, high, label in prob_bins:
        mask = (df['win_probability'] >= low) & (df['win_probability'] < high)
        subset = df[mask]
        if len(subset) == 0:
            continue

        subset_wins = (subset['actual_win'] == 1).sum()
        subset_roi = subset['profit'].sum() / subset['bet_amount'].sum() * 100

        print(f"{label:20s} {len(subset):>6} {subset_wins:>6} "
              f"{subset_wins / len(subset) * 100:>6.1f}% {subset_roi:>+7.1f}%")

    # Find best performing segment
    print("\n📊 ONLY BET HIGH CONFIDENCE (>25% probability):")
    high_conf = df[df['win_probability'] >= 0.25]
    if len(high_conf) > 0:
        hc_wins = (high_conf['actual_win'] == 1).sum()
        hc_roi = high_conf['profit'].sum() / high_conf['bet_amount'].sum() * 100
        print(f"  Bets: {len(high_conf)}, Wins: {hc_wins} ({hc_wins / len(high_conf) * 100:.1f}%)")
        print(f"  ROI: {hc_roi:+.1f}%")

    # Calibration check
    print("\n📊 MODEL CALIBRATION CHECK:")
    print("(Does predicted probability match actual win rate?)")
    print(f"{'Pred Prob':15s} {'Actual Win%':>12} {'Calibration':>12}")
    print("-" * 42)

    for low, high, label in prob_bins:
        mask = (df['win_probability'] >= low) & (df['win_probability'] < high)
        subset = df[mask]
        if len(subset) < 5:
            continue

        actual_win_rate = (subset['actual_win'] == 1).mean() * 100
        pred_prob = subset['win_probability'].mean() * 100
        calibration = actual_win_rate - pred_prob

        print(f"{label:15s} {actual_win_rate:>11.1f}% {calibration:>+11.1f}%")

    print("\n✓ Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    analyze_backtest_results()