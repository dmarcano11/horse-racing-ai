"""XGBoost model for horse racing prediction."""
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
from imblearn.over_sampling import SMOTE
import joblib
import logging

from src.ml.data_preparation import DataPreparation
from src.ml.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class XGBoostModel:
    """XGBoost classifier."""

    def __init__(
            self,
            n_estimators: int = 100,
            max_depth: int = 6,
            learning_rate: float = 0.1,
            use_smote: bool = True,
            random_state: int = 42
    ):
        """
        Initialize XGBoost model.

        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum depth of trees
            learning_rate: Learning rate
            use_smote: Whether to use SMOTE
            random_state: Random seed
        """
        self.use_smote = use_smote
        self.random_state = random_state

        # Calculate scale_pos_weight for imbalanced data
        # This will be updated during training
        self.scale_pos_weight = 1.0

        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            scale_pos_weight=self.scale_pos_weight,
            random_state=random_state,
            eval_metric='logloss',
            use_label_encoder=False,
            n_jobs=-1
        )

        self.smote = SMOTE(random_state=random_state) if use_smote else None
        self.evaluator = ModelEvaluator()
        self.feature_names = None

    def train(self, X_train, y_train):
        """
        Train the model.

        Args:
            X_train: Training features
            y_train: Training targets
        """
        logger.info("Training XGBoost model...")
        logger.info(f"  Estimators: {self.model.n_estimators}")
        logger.info(f"  Max depth: {self.model.max_depth}")
        logger.info(f"  Learning rate: {self.model.learning_rate}")

        # Store feature names
        if hasattr(X_train, 'columns'):
            self.feature_names = X_train.columns.tolist()

        # Apply SMOTE if enabled
        if self.use_smote:
            logger.info("Applying SMOTE for class balance...")
            X_train_resampled, y_train_resampled = self.smote.fit_resample(X_train, y_train)
            logger.info(f"  Original: {len(y_train)} samples")
            logger.info(f"  Resampled: {len(y_train_resampled)} samples")
        else:
            X_train_resampled = X_train
            y_train_resampled = y_train

            # Calculate scale_pos_weight for imbalanced data
            n_neg = (y_train_resampled == 0).sum()
            n_pos = (y_train_resampled == 1).sum()
            self.scale_pos_weight = n_neg / n_pos
            self.model.set_params(scale_pos_weight=self.scale_pos_weight)
            logger.info(f"  Scale pos weight: {self.scale_pos_weight:.2f}")

        # Train model
        self.model.fit(X_train_resampled, y_train_resampled)
        logger.info("✓ Model trained")

    def predict(self, X):
        """Predict class labels."""
        return self.model.predict(X)

    def predict_proba(self, X):
        """Predict probabilities."""
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X_test, y_test):
        """
        Evaluate the model.

        Args:
            X_test: Test features
            y_test: Test targets

        Returns:
            Dictionary of metrics
        """
        y_pred = self.predict(X_test)
        y_pred_proba = self.predict_proba(X_test)

        metrics = self.evaluator.evaluate_binary_classifier(
            y_test, y_pred, y_pred_proba,
            model_name="XGBoost"
        )

        self.evaluator.print_classification_report(
            y_test, y_pred,
            model_name="XGBoost"
        )

        return metrics

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from trained model.

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature importance
        """
        if self.feature_names is None:
            logger.warning("Feature names not available")
            return pd.DataFrame()

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance_df.head(top_n)

    def save_model(self, filepath: Path):
        """Save model to disk."""
        joblib.dump(self.model, filepath)
        logger.info(f"Saved model to {filepath}")

    def load_model(self, filepath: Path):
        """Load model from disk."""
        self.model = joblib.load(filepath)
        logger.info(f"Loaded model from {filepath}")


def run_xgboost():
    """Run XGBoost model pipeline."""
    from src.utils.logger import setup_logging
    setup_logging("xgboost")

    # Prepare data
    data_prep = DataPreparation()
    data_path = Path("data/processed/features_sample.csv")

    data = data_prep.prepare_ml_data(data_path, train_ratio=0.8, scale=True)

    # Train model
    model = XGBoostModel(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        use_smote=True
    )
    model.train(data['X_train'], data['y_train'])

    # Evaluate
    metrics = model.evaluate(data['X_test'], data['y_test'])

    # Feature importance
    importance_df = model.get_feature_importance(top_n=20)
    print("\n" + "=" * 60)
    print("TOP 20 MOST IMPORTANT FEATURES (XGBoost)")
    print("=" * 60)
    for idx, row in importance_df.iterrows():
        print(f"{row['feature']:40s} {row['importance']:.4f}")
    print("=" * 60)

    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    model.save_model(model_dir / "xgboost.pkl")

    print("\n" + "=" * 80)
    print("✓ XGBOOST MODEL COMPLETE")
    print("=" * 80)
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    print(f"Test F1 Score: {metrics['f1']:.4f}")
    print(f"Test ROC-AUC:  {metrics['roc_auc']:.4f}")
    print("=" * 80)

    return model, metrics


if __name__ == "__main__":
    run_xgboost()