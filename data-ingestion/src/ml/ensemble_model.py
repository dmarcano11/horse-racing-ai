"""Ensemble model combining tuned models."""
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from sklearn.ensemble import VotingClassifier
from src.ml.data_preparation import DataPreparation
from src.ml.evaluation import ModelEvaluator
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


class EnsembleModel:
    """Ensemble model combining multiple classifiers."""

    def __init__(self, models_dict: dict, voting: str = 'soft'):
        """
        Initialize ensemble.

        Args:
            models_dict: Dictionary of {name: model}
            voting: 'soft' (probabilities) or 'hard' (majority vote)
        """
        self.models_dict = models_dict
        self.voting = voting
        self.evaluator = ModelEvaluator()

        # Create voting classifier
        estimators = [(name, model) for name, model in models_dict.items()]
        self.ensemble = VotingClassifier(
            estimators=estimators,
            voting=voting,
            n_jobs=-1
        )

    def train(self, X_train, y_train):
        """Train ensemble (fits all underlying models)."""
        logger.info("Training ensemble model...")
        logger.info(f"  Models: {list(self.models_dict.keys())}")
        logger.info(f"  Voting: {self.voting}")

        self.ensemble.fit(X_train, y_train)
        logger.info("✓ Ensemble trained")

    def predict(self, X):
        """Predict class labels."""
        return self.ensemble.predict(X)

    def predict_proba(self, X):
        """Predict probabilities."""
        return self.ensemble.predict_proba(X)[:, 1]

    def evaluate(self, X_test, y_test):
        """Evaluate ensemble."""
        y_pred = self.predict(X_test)
        y_pred_proba = self.predict_proba(X_test)

        metrics = self.evaluator.evaluate_binary_classifier(
            y_test, y_pred, y_pred_proba,
            model_name="Ensemble (Voting)"
        )

        self.evaluator.print_classification_report(
            y_test, y_pred,
            model_name="Ensemble"
        )

        return metrics

    def get_individual_predictions(self, X):
        """Get predictions from each individual model."""
        predictions = {}

        for name, model in self.models_dict.items():
            predictions[name] = {
                'pred': model.predict(X),
                'proba': model.predict_proba(X)[:, 1]
            }

        return predictions

    def save_model(self, filepath: Path):
        """Save ensemble model."""
        joblib.dump(self.ensemble, filepath)
        logger.info(f"Saved ensemble to {filepath}")


def load_tuned_models(models_dir: Path) -> dict:
    """Load tuned models from disk."""
    models = {}

    model_files = {
        'Logistic Regression': 'logistic_regression_tuned.pkl',
        'Random Forest': 'random_forest_tuned.pkl',
        'XGBoost': 'xgboost_tuned.pkl'
    }

    for name, filename in model_files.items():
        filepath = models_dir / filename
        if filepath.exists():
            models[name] = joblib.load(filepath)
            logger.info(f"Loaded {name} from {filepath}")
        else:
            logger.warning(f"Model file not found: {filepath}")

    return models


def run_ensemble():
    """Run ensemble model pipeline."""
    setup_logging("ensemble")

    print("\n" + "=" * 80)
    print("ENSEMBLE MODEL - COMBINING TUNED MODELS")
    print("=" * 80)

    # Load tuned models
    models_dir = Path("models/tuned")

    if not models_dir.exists():
        print("\n❌ Tuned models not found!")
        print("Please run hyperparameter tuning first:")
        print("  python -m src.ml.hyperparameter_tuning")
        return

    models = load_tuned_models(models_dir)

    if len(models) == 0:
        print("\n❌ No tuned models loaded!")
        return

    # Prepare data
    data_prep = DataPreparation()
    data = data_prep.prepare_ml_data(
        Path("data/processed/features_complete.csv"),
        train_ratio=0.8,
        scale=True
    )

    # Create and train ensemble
    ensemble = EnsembleModel(models, voting='soft')
    ensemble.train(data['X_train'], data['y_train'])

    # Evaluate ensemble
    ensemble_metrics = ensemble.evaluate(data['X_test'], data['y_test'])

    # Also evaluate individual models for comparison
    print("\n" + "=" * 80)
    print("INDIVIDUAL MODEL PERFORMANCE (on test set)")
    print("=" * 80)

    individual_results = {}
    evaluator = ModelEvaluator()

    for name, model in models.items():
        y_pred = model.predict(data['X_test'])
        y_pred_proba = model.predict_proba(data['X_test'])[:, 1]

        metrics = evaluator.evaluate_binary_classifier(
            data['y_test'], y_pred, y_pred_proba,
            model_name=name
        )

        individual_results[name] = metrics

    # Add ensemble
    individual_results['Ensemble'] = ensemble_metrics

    # Compare all
    comparison_df = evaluator.compare_models(individual_results)

    # Save ensemble
    output_dir = Path("models/ensemble")
    output_dir.mkdir(exist_ok=True, parents=True)
    ensemble.save_model(output_dir / "voting_ensemble.pkl")

    # Save comparison
    comparison_df.to_csv("data/processed/ensemble_comparison.csv")

    print("\n" + "=" * 80)
    print("✓ ENSEMBLE MODEL COMPLETE")
    print("=" * 80)
    print(f"Ensemble ROC-AUC: {ensemble_metrics['roc_auc']:.4f}")
    print("\nSaved to: models/ensemble/voting_ensemble.pkl")
    print("Comparison saved to: data/processed/ensemble_comparison.csv")
    print("=" * 80)

    return ensemble, comparison_df


if __name__ == "__main__":
    run_ensemble()