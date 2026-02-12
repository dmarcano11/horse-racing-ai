"""ML Predictor - loads model and generates predictions."""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

# Paths - relative to ml-service directory
MODEL_PATH = Path("../data-ingestion/models/tuned/random_forest_tuned.pkl")
FEATURES_PATH = Path("../data-ingestion/data/processed/features_complete.csv")


class HorseRacingPredictor:
    """Generates win probability predictions for horse races."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_loaded = False

    def load(self):
        """Load model and fit scaler on training data."""
        try:
            # Load model
            logger.info(f"Loading model from {MODEL_PATH}")
            self.model = joblib.load(MODEL_PATH)

            # Load training data to fit scaler
            logger.info(f"Loading features from {FEATURES_PATH}")
            df = pd.read_csv(FEATURES_PATH)

            # Get feature columns (same logic as training)
            exclude_cols = [
                'runner_id', 'race_id', 'meet_id',
                'target_win', 'target_finish_position'
            ]
            self.feature_columns = [
                col for col in df.columns
                if col not in exclude_cols
                and df[col].dtype in ['float64', 'int64']
            ]

            # Fit scaler on training portion (first 80%)
            df_complete = df[df['target_win'] >= 0].copy()
            df_sorted = df_complete.sort_values('race_id')
            split_idx = int(len(df_sorted) * 0.8)
            train_df = df_sorted.iloc[:split_idx]

            self.scaler.fit(train_df[self.feature_columns])

            self.is_loaded = True
            logger.info(f"✓ Model loaded with {len(self.feature_columns)} features")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def predict_race(self, runners: list) -> list:
        """
        Generate win probabilities for all runners in a race.

        Args:
            runners: List of runner dicts with feature values

        Returns:
            List of predictions with runner_id and win_probability
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        if not runners:
            return []

        # Build feature DataFrame
        rows = []
        runner_ids = []

        for runner in runners:
            runner_ids.append(runner.get('runner_id'))
            row = {}
            for col in self.feature_columns:
                row[col] = runner.get(col, 0.0) or 0.0
            rows.append(row)

        X = pd.DataFrame(rows, columns=self.feature_columns)

        # Fill any missing values with 0
        X = X.fillna(0.0)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Get win probabilities
        probabilities = self.model.predict_proba(X_scaled)[:, 1]

        # Normalize probabilities to sum to 1.0 within the race
        total_prob = probabilities.sum()
        if total_prob > 0:
            normalized_probs = probabilities / total_prob
        else:
            normalized_probs = np.ones(len(probabilities)) / len(probabilities)

        # Build results
        results = []
        for i, runner_id in enumerate(runner_ids):
            results.append({
                'runner_id': runner_id,
                'win_probability': round(float(probabilities[i]), 4),
                'win_probability_normalized': round(float(normalized_probs[i]), 4),
                'implied_odds': round(1.0 / float(probabilities[i]) - 1, 2)
                    if probabilities[i] > 0 else 99.0
            })

        # Sort by win probability descending
        results.sort(key=lambda x: x['win_probability'], reverse=True)

        # Add rank
        for i, result in enumerate(results):
            result['model_rank'] = i + 1

        return results

    def health_check(self) -> dict:
        """Return model health status."""
        return {
            'status': 'healthy' if self.is_loaded else 'not_loaded',
            'model_loaded': self.is_loaded,
            'feature_count': len(self.feature_columns) if self.feature_columns else 0,
            'model_type': type(self.model).__name__ if self.model else None
        }


# Singleton instance
predictor = HorseRacingPredictor()