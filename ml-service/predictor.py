"""ML Predictor - loads model and generates real feature-based predictions."""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text
import logging
import os

logger = logging.getLogger(__name__)

MODEL_PATH = Path("../data-ingestion/models/tuned/random_forest_tuned.pkl")
FEATURES_PATH = Path("../data-ingestion/data/processed/features_complete.csv")

DB_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://racing_user:racing_dev_password@localhost:5433/racing_db'
)

class HorseRacingPredictor:
    """Generates win probability predictions using real features."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_loaded = False
        self.engine = None

    def load(self):
        """Load model, fit scaler, connect to database."""
        try:
            # Load model
            logger.info(f"Loading model from {MODEL_PATH}")
            self.model = joblib.load(MODEL_PATH)

            # Load training data to fit scaler
            logger.info(f"Loading features from {FEATURES_PATH}")
            df = pd.read_csv(FEATURES_PATH)

            exclude_cols = [
                'runner_id', 'race_id', 'meet_id',
                'target_win', 'target_finish_position'
            ]
            self.feature_columns = [
                col for col in df.columns
                if col not in exclude_cols
                and df[col].dtype in ['float64', 'int64']
            ]

            # Fit scaler on training portion only
            df_complete = df[df['target_win'] >= 0].copy()
            df_sorted = df_complete.sort_values('race_id')
            split_idx = int(len(df_sorted) * 0.8)
            train_df = df_sorted.iloc[:split_idx]
            self.scaler.fit(train_df[self.feature_columns])

            # Connect to database
            logger.info("Connecting to database...")
            self.engine = create_engine(DB_URL)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Database connected")

            self.is_loaded = True
            logger.info(f"✓ Model loaded with {len(self.feature_columns)} features")

        except Exception as e:
            logger.error(f"Failed to load: {e}")
            raise

    def get_race_features(self, race_id: int) -> pd.DataFrame:
        """
        Fetch runners and calculate features for a race.
        Uses the same feature engineering as training.
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data-ingestion'))

        from src.db.session import get_db_context
        from src.features.feature_builder import FeatureBuilder
        from src.db.models import Race, Meet

        with get_db_context() as db:
            # Get race
            race = db.query(Race).filter(Race.id == race_id).first()
            if not race:
                raise ValueError(f"Race {race_id} not found")

            meet = db.query(Meet).filter(Meet.id == race.meet_id).first()

            # Build features
            builder = FeatureBuilder(db)
            race_features = builder.build_features_for_race(race, meet)

            return race_features

    def predict_race_from_db(self, race_id: int) -> list:
        """
        Generate predictions for a race using full feature engineering.

        Args:
            race_id: Database race ID

        Returns:
            List of predictions sorted by win probability
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        try:
            # Get real features from database
            logger.info(f"Building features for race {race_id}")
            df = self.get_race_features(race_id)

            if df.empty:
                logger.warning(f"No features built for race {race_id}")
                return []

            # Get runner IDs
            runner_ids = df['runner_id'].tolist()

            # Get feature matrix
            available_features = [
                col for col in self.feature_columns
                if col in df.columns
            ]

            missing_features = [
                col for col in self.feature_columns
                if col not in df.columns
            ]

            if missing_features:
                logger.warning(f"Missing {len(missing_features)} features: {missing_features[:5]}...")
                for col in missing_features:
                    df[col] = 0.0

            X = df[self.feature_columns].fillna(0.0)

            # Scale and predict
            X_scaled = self.scaler.transform(X)
            probabilities = self.model.predict_proba(X_scaled)[:, 1]

            # Normalize within race
            total_prob = probabilities.sum()
            normalized_probs = probabilities / total_prob if total_prob > 0 \
                else np.ones(len(probabilities)) / len(probabilities)

            # Build results
            results = []
            for i, runner_id in enumerate(runner_ids):
                results.append({
                    'runner_id': int(runner_id),
                    'win_probability': round(float(probabilities[i]), 4),
                    'win_probability_normalized': round(float(normalized_probs[i]), 4),
                    'implied_odds': round(1.0 / float(probabilities[i]) - 1, 2)
                        if probabilities[i] > 0 else 99.0,
                    'features_used': len(available_features),
                    'using_real_features': True
                })

            results.sort(key=lambda x: x['win_probability'], reverse=True)
            for i, r in enumerate(results):
                r['model_rank'] = i + 1

            logger.info(f"✓ Generated {len(results)} predictions for race {race_id}")
            return results

        except Exception as e:
            logger.error(f"Feature-based prediction failed: {e}")
            logger.info("Falling back to basic prediction")
            raise

    def predict_race(self, runners: list) -> list:
        """Fallback: predict from provided feature dict (basic mode)."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        if not runners:
            return []

        rows = []
        runner_ids = []

        for runner in runners:
            runner_ids.append(runner.get('runner_id'))
            row = {col: runner.get(col, 0.0) or 0.0
                   for col in self.feature_columns}
            rows.append(row)

        X = pd.DataFrame(rows, columns=self.feature_columns).fillna(0.0)
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]

        total_prob = probabilities.sum()
        normalized_probs = probabilities / total_prob if total_prob > 0 \
            else np.ones(len(probabilities)) / len(probabilities)

        results = []
        for i, runner_id in enumerate(runner_ids):
            results.append({
                'runner_id': runner_id,
                'win_probability': round(float(probabilities[i]), 4),
                'win_probability_normalized': round(float(normalized_probs[i]), 4),
                'implied_odds': round(1.0 / float(probabilities[i]) - 1, 2)
                    if probabilities[i] > 0 else 99.0,
                'using_real_features': False
            })

        results.sort(key=lambda x: x['win_probability'], reverse=True)
        for i, r in enumerate(results):
            r['model_rank'] = i + 1

        return results

    def health_check(self) -> dict:
        """Return health status."""
        return {
            'status': 'healthy' if self.is_loaded else 'not_loaded',
            'model_loaded': self.is_loaded,
            'feature_count': len(self.feature_columns) if self.feature_columns else 0,
            'model_type': type(self.model).__name__ if self.model else None,
            'database_connected': self.engine is not None
        }


predictor = HorseRacingPredictor()