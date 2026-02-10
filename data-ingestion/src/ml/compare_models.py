"""Compare all models."""
from pathlib import Path
import pandas as pd
from src.utils.logger import setup_logging

from src.ml.data_preparation import DataPreparation
from src.ml.baseline_model import BaselineModel
from src.ml.random_forest_model import RandomForestModel
from src.ml.xgboost_model import XGBoostModel
from src.ml.evaluation import ModelEvaluator


def compare_all_models():
    """Train and compare all models."""
    setup_logging("model_comparison")

    # Prepare data
    print("\n" + "=" * 80)
    print("PREPARING DATA")
    print("=" * 80)

    data_prep = DataPreparation()
    data_path = Path("data/processed/features_sample.csv")
    data = data_prep.prepare_ml_data(data_path, train_ratio=0.8, scale=True)

    results = {}

    # 1. Logistic Regression (Baseline)
    print("\n" + "=" * 80)
    print("1. TRAINING LOGISTIC REGRESSION")
    print("=" * 80)

    lr_model = BaselineModel(use_smote=True, class_weight='balanced')
    lr_model.train(data['X_train'], data['y_train'])
    results['Logistic Regression'] = lr_model.evaluate(data['X_test'], data['y_test'])

    # 2. Random Forest
    print("\n" + "=" * 80)
    print("2. TRAINING RANDOM FOREST")
    print("=" * 80)

    rf_model = RandomForestModel(
        n_estimators=100,
        max_depth=10,
        use_smote=True,
        class_weight='balanced'
    )
    rf_model.train(data['X_train'], data['y_train'])
    results['Random Forest'] = rf_model.evaluate(data['X_test'], data['y_test'])

    # 3. XGBoost
    print("\n" + "=" * 80)
    print("3. TRAINING XGBOOST")
    print("=" * 80)

    xgb_model = XGBoostModel(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        use_smote=True
    )
    xgb_model.train(data['X_train'], data['y_train'])
    results['XGBoost'] = xgb_model.evaluate(data['X_test'], data['y_test'])

    # Compare models
    evaluator = ModelEvaluator()
    comparison_df = evaluator.compare_models(results)

    # Save comparison
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True, parents=True)
    comparison_df.to_csv(output_dir / "model_comparison.csv")

    print("\n✓ Model comparison saved to data/processed/model_comparison.csv")

    # Determine best model
    best_model_name = comparison_df.index[0]
    best_roc_auc = comparison_df.loc[best_model_name, 'roc_auc']

    print("\n" + "=" * 80)
    print(f"🏆 BEST MODEL: {best_model_name}")
    print(f"   ROC-AUC: {best_roc_auc:.4f}")
    print("=" * 80)

    return results, comparison_df


if __name__ == "__main__":
    compare_all_models()