"""Baseline model - Logistic Regression."""
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
import joblib
import logging

from src.ml.data_preparation import DataPreparation
from src.ml.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class BaselineModel:
    """Logistic Regression baseline model."""

    def __init__(
            self,
            use_smote: bool = True,
            class_weight: str = 'balanced',
            random_state: int = 42
    ):
        """
        Initialize baseline model.

        Args:
            use_smote: Whether to use SMOTE for class imbalance
            class_weight: Class weight strategy ('balanced' or None)
            random_state: Random seed
        """
        self.use_smote = use_smote
        self.class_weight = class_weight
        self.random_state = random_state

        self.model = LogisticRegression(
            class_weight=class_weight,
            random_state=random_state,
            max_iter=1000,
            solver='lbfgs'
        )

        self.smote = SMOTE(random_state=random_state) if use_smote else None
        self.evaluator = ModelEvaluator()

    def train(self, X_train, y_train):
        """
        Train the model.

        Args:
            X_train: Training features
            y_train: Training targets
        """
        logger.info("Training Logistic Regression model...")

        # Apply SMOTE if enabled
        if self.use_smote:
            logger.info("Applying SMOTE for class balance...")
            X_train_resampled, y_train_resampled = self.smote.fit_resample(X_train, y_train)
            logger.info(f"  Original: {len(y_train)} samples")
            logger.info(f"  Resampled: {len(y_train_resampled)} samples")
            logger.info(f"  Class 0: {(y_train_resampled == 0).sum()}")
            logger.info(f"  Class 1: {(y_train_resampled == 1).sum()}")
        else:
            X_train_resampled = X_train
            y_train_resampled = y_train

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
            model_name="Logistic Regression (Baseline)"
        )

        self.evaluator.print_classification_report(
            y_test, y_pred,
            model_name="Logistic Regression"
        )

        return metrics

    def save_model(self, filepath: Path):
        """Save model to disk."""
        joblib.dump(self.model, filepath)
        logger.info(f"Saved model to {filepath}")

    def load_model(self, filepath: Path):
        """Load model from disk."""
        self.model = joblib.load(filepath)
        logger.info(f"Loaded model from {filepath}")


def run_baseline():
    """Run baseline model pipeline."""
    from src.utils.logger import setup_logging
    setup_logging("baseline_model")

    # Prepare data
    data_prep = DataPreparation()
    data_path = Path("data/processed/features_sample.csv")

    data = data_prep.prepare_ml_data(data_path, train_ratio=0.8, scale=True)

    # Train model
    model = BaselineModel(use_smote=True, class_weight='balanced')
    model.train(data['X_train'], data['y_train'])

    # Evaluate
    metrics = model.evaluate(data['X_test'], data['y_test'])

    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    model.save_model(model_dir / "baseline_logistic_regression.pkl")

    print("\n" + "=" * 80)
    print("✓ BASELINE MODEL COMPLETE")
    print("=" * 80)
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    print(f"Test F1 Score: {metrics['f1']:.4f}")
    print(f"Test ROC-AUC:  {metrics['roc_auc']:.4f}")
    print("=" * 80)

    return model, metrics


if __name__ == "__main__":
    run_baseline()