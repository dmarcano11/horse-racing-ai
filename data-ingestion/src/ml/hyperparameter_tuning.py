"""Hyperparameter tuning for all models."""
from pathlib import Path
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import numpy as np
import pandas as pd
import joblib
from src.ml.data_preparation import DataPreparation
from src.ml.evaluation import ModelEvaluator
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """Hyperparameter tuning for all models."""

    def __init__(self, data, use_randomized: bool = False, n_iter: int = 50):
        """
        Initialize tuner.

        Args:
            data: Prepared data dictionary
            use_randomized: Use RandomizedSearchCV instead of GridSearchCV
            n_iter: Number of iterations for randomized search
        """
        self.data = data
        self.use_randomized = use_randomized
        self.n_iter = n_iter
        self.evaluator = ModelEvaluator()

        self.best_models = {}
        self.best_params = {}
        self.cv_results = {}

    def tune_logistic_regression(self):
        """
        Tune Logistic Regression.

        Parameters to tune:
        - C: Regularization strength (inverse)
        - penalty: L1 or L2 regularization
        - solver: Optimization algorithm
        """
        logger.info("\n" + "=" * 80)
        logger.info("TUNING LOGISTIC REGRESSION")
        logger.info("=" * 80)

        # Parameter grid
        param_grid = {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'penalty': ['l2'],  # l1 requires saga solver
            'solver': ['lbfgs', 'liblinear'],
            'class_weight': ['balanced', None],
            'max_iter': [1000]
        }

        # Base model
        lr = LogisticRegression(random_state=42)

        # Search
        if self.use_randomized:
            search = RandomizedSearchCV(
                lr, param_grid, n_iter=self.n_iter,
                cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42
            )
        else:
            search = GridSearchCV(
                lr, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
            )

        search.fit(self.data['X_train'], self.data['y_train'])

        self.best_models['Logistic Regression'] = search.best_estimator_
        self.best_params['Logistic Regression'] = search.best_params_
        self.cv_results['Logistic Regression'] = search.cv_results_

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best CV ROC-AUC: {search.best_score_:.4f}")

        return search.best_estimator_, search.best_params_

    def tune_random_forest(self):
        """
        Tune Random Forest.

        Parameters to tune:
        - n_estimators: Number of trees
        - max_depth: Maximum tree depth
        - min_samples_split: Minimum samples to split node
        - min_samples_leaf: Minimum samples per leaf
        - max_features: Features to consider at each split
        """
        logger.info("\n" + "=" * 80)
        logger.info("TUNING RANDOM FOREST")
        logger.info("=" * 80)

        if self.use_randomized:
            # Larger search space for randomized search
            param_grid = {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [5, 10, 15, 20, 25, None],
                'min_samples_split': [2, 5, 10, 15],
                'min_samples_leaf': [1, 2, 4, 8],
                'max_features': ['sqrt', 'log2', None],
                'class_weight': ['balanced', 'balanced_subsample']
            }
        else:
            # Smaller grid for exhaustive search
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, 20],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2'],
                'class_weight': ['balanced', 'balanced_subsample']
            }

        # Base model
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)

        # Search
        if self.use_randomized:
            search = RandomizedSearchCV(
                rf, param_grid, n_iter=self.n_iter,
                cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42
            )
        else:
            search = GridSearchCV(
                rf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
            )

        search.fit(self.data['X_train'], self.data['y_train'])

        self.best_models['Random Forest'] = search.best_estimator_
        self.best_params['Random Forest'] = search.best_params_
        self.cv_results['Random Forest'] = search.cv_results_

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best CV ROC-AUC: {search.best_score_:.4f}")

        return search.best_estimator_, search.best_params_

    def tune_xgboost(self):
        """
        Tune XGBoost.

        Parameters to tune:
        - n_estimators: Number of boosting rounds
        - max_depth: Maximum tree depth
        - learning_rate: Step size shrinkage
        - subsample: Subsample ratio of training data
        - colsample_bytree: Subsample ratio of features
        """
        logger.info("\n" + "=" * 80)
        logger.info("TUNING XGBOOST")
        logger.info("=" * 80)

        if self.use_randomized:
            # Larger search space
            param_grid = {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [3, 5, 7, 9, 11],
                'learning_rate': [0.01, 0.05, 0.1, 0.2, 0.3],
                'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
                'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0],
                'gamma': [0, 0.1, 0.2, 0.3],
                'min_child_weight': [1, 3, 5, 7]
            }
        else:
            # Smaller grid
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.7, 0.8, 1.0],
                'colsample_bytree': [0.7, 0.8, 1.0],
                'gamma': [0, 0.1]
            }

        # Base model
        xgb_model = xgb.XGBClassifier(
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False,
            n_jobs=-1
        )

        # Search
        if self.use_randomized:
            search = RandomizedSearchCV(
                xgb_model, param_grid, n_iter=self.n_iter,
                cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42
            )
        else:
            search = GridSearchCV(
                xgb_model, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1
            )

        search.fit(self.data['X_train'], self.data['y_train'])

        self.best_models['XGBoost'] = search.best_estimator_
        self.best_params['XGBoost'] = search.best_params_
        self.cv_results['XGBoost'] = search.cv_results_

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best CV ROC-AUC: {search.best_score_:.4f}")

        return search.best_estimator_, search.best_params_

    def tune_all_models(self):
        """Tune all three models."""
        logger.info("=" * 80)
        logger.info("HYPERPARAMETER TUNING - ALL MODELS")
        logger.info("=" * 80)

        # Tune each model
        self.tune_logistic_regression()
        self.tune_random_forest()
        self.tune_xgboost()

        # Evaluate all on test set
        results = {}

        for model_name, model in self.best_models.items():
            y_pred = model.predict(self.data['X_test'])
            y_pred_proba = model.predict_proba(self.data['X_test'])[:, 1]

            metrics = self.evaluator.evaluate_binary_classifier(
                self.data['y_test'], y_pred, y_pred_proba,
                model_name=f"{model_name} (Tuned)"
            )

            results[model_name] = metrics

        # Compare
        comparison_df = self.evaluator.compare_models(results)

        # Print best parameters
        print("\n" + "=" * 80)
        print("BEST HYPERPARAMETERS FOR EACH MODEL")
        print("=" * 80)

        for model_name, params in self.best_params.items():
            print(f"\n{model_name}:")
            for param, value in params.items():
                print(f"  {param:20s}: {value}")

        print("\n" + "=" * 80)

        return self.best_models, self.best_params, comparison_df

    def save_tuned_models(self, output_dir: Path):
        """Save tuned models to disk."""
        output_dir.mkdir(exist_ok=True, parents=True)

        for model_name, model in self.best_models.items():
            # Clean filename
            filename = model_name.lower().replace(' ', '_') + '_tuned.pkl'
            filepath = output_dir / filename

            joblib.dump(model, filepath)
            logger.info(f"Saved {model_name} to {filepath}")

        # Save parameters as JSON
        params_path = output_dir / 'best_hyperparameters.json'
        import json
        with open(params_path, 'w') as f:
            # Convert numpy types to Python types for JSON
            params_json = {}
            for model_name, params in self.best_params.items():
                params_json[model_name] = {k: str(v) for k, v in params.items()}
            json.dump(params_json, f, indent=2)

        logger.info(f"Saved hyperparameters to {params_path}")


def run_hyperparameter_tuning(use_randomized: bool = False):
    """
    Run hyperparameter tuning pipeline.

    Args:
        use_randomized: Use RandomizedSearchCV (faster) vs GridSearchCV (exhaustive)
    """
    setup_logging("hyperparameter_tuning")

    # Prepare data
    logger.info("Loading data...")
    data_prep = DataPreparation()
    data = data_prep.prepare_ml_data(
        Path("data/processed/features_complete.csv"),
        train_ratio=0.8,
        scale=True
    )

    # Tune models
    tuner = HyperparameterTuner(data, use_randomized=use_randomized, n_iter=50)
    best_models, best_params, comparison_df = tuner.tune_all_models()

    # Save models
    tuner.save_tuned_models(Path("models/tuned"))

    # Save comparison
    comparison_df.to_csv("data/processed/tuned_models_comparison.csv")

    print("\n" + "=" * 80)
    print("✓ HYPERPARAMETER TUNING COMPLETE")
    print("=" * 80)
    print("\nTuned models saved to: models/tuned/")
    print("Comparison saved to: data/processed/tuned_models_comparison.csv")
    print("=" * 80)

    return best_models, best_params


if __name__ == "__main__":
    # Use randomized=True for faster tuning, False for exhaustive search
    # Randomized is recommended for first pass
    run_hyperparameter_tuning(use_randomized=True)