"""Random Forest model for horse racing prediction."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import joblib
import logging
import matplotlib.pyplot as plt

from src.ml.data_preparation import DataPreparation
from src.ml.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class RandomForestModel:
    """Random Forest classifier."""

    def __init__(
            self,
            n_estimators: int = 100,
            max_depth: int = 10,
            min_samples_split: int = 5,
            min_samples_leaf: int = 2,
            use_smote: bool = True,
            class_weight: str = 'balanced',
            random_state: int = 42
    ):
        """
        Initialize Random Forest model.

        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples to split
            min_samples_leaf: Minimum samples per leaf
            use_smote: Whether to use SMOTE
            class_weight: Class weight strategy
            random_state: Random seed
        """
        self.use_smote = use_smote
        self.random_state = random_state

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1  # Use all CPU cores
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
        logger.info("Training Random Forest model...")
        logger.info(f"  Trees: {self.model.n_estimators}")
        logger.info(f"  Max depth: {self.model.max_depth}")

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
            model_name="Random Forest"
        )

        self.evaluator.print_classification_report(
            y_test, y_pred,
            model_name="Random Forest"
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

    def plot_feature_importance(self, top_n: int = 20, save_path: str = None):
        """
        Plot feature importance.

        Args:
            top_n: Number of top features to show
            save_path: Path to save plot
        """
        importance_df = self.get_feature_importance(top_n)

        if importance_df.empty:
            logger.warning("No feature importance to plot")
            return

        plt.figure(figsize=(10, 8))
        plt.barh(range(len(importance_df)), importance_df['importance'])
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('Importance')
        plt.title(f'Top {top_n} Feature Importances - Random Forest')
        plt.gca().invert_yaxis()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved feature importance plot to {save_path}")

        plt.show()

        # Print top features
        print("\n" + "=" * 60)
        print(f"TOP {top_n} MOST IMPORTANT FEATURES")
        print("=" * 60)
        for idx, row in importance_df.iterrows():
            print(f"{row['feature']:40s} {row['importance']:.4f}")
        print("=" * 60)

    def save_model(self, filepath: Path):
        """Save model to disk."""
        joblib.dump(self.model, filepath)
        logger.info(f"Saved model to {filepath}")

    def load_model(self, filepath: Path):
        """Load model from disk."""
        self.model = joblib.load(filepath)
        logger.info(f"Loaded model from {filepath}")


def run_random_forest():
    """Run Random Forest model pipeline."""
    from src.utils.logger import setup_logging
    setup_logging("random_forest")

    # Prepare data
    data_prep = DataPreparation()
    data_path = Path("data/processed/features_sample.csv")

    data = data_prep.prepare_ml_data(data_path, train_ratio=0.8, scale=True)

    # Train model
    model = RandomForestModel(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        use_smote=True,
        class_weight='balanced'
    )
    model.train(data['X_train'], data['y_train'])

    # Evaluate
    metrics = model.evaluate(data['X_test'], data['y_test'])

    # Feature importance
    model.plot_feature_importance(top_n=20)

    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    model.save_model(model_dir / "random_forest.pkl")

    print("\n" + "=" * 80)
    print("✓ RANDOM FOREST MODEL COMPLETE")
    print("=" * 80)
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    print(f"Test F1 Score: {metrics['f1']:.4f}")
    print(f"Test ROC-AUC:  {metrics['roc_auc']:.4f}")
    print("=" * 80)

    return model, metrics


if __name__ == "__main__":
    run_random_forest()