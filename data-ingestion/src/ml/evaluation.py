"""Model evaluation utilities."""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate ML model performance."""

    def evaluate_binary_classifier(
            self,
            y_true: np.ndarray,
            y_pred: np.ndarray,
            y_pred_proba: Optional[np.ndarray] = None,
            model_name: str = "Model"
    ) -> Dict[str, float]:
        """
        Evaluate binary classification model.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (for ROC-AUC)
            model_name: Name of the model

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
        metrics['f1'] = f1_score(y_true, y_pred, zero_division=0)

        # ROC-AUC (if probabilities provided)
        if y_pred_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()

        metrics['true_negatives'] = int(tn)
        metrics['false_positives'] = int(fp)
        metrics['false_negatives'] = int(fn)
        metrics['true_positives'] = int(tp)

        # Additional metrics
        metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0

        # Log results
        logger.info(f"\n{model_name} Performance:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1 Score:  {metrics['f1']:.4f}")
        if 'roc_auc' in metrics:
            logger.info(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")

        return metrics

    def print_classification_report(
            self,
            y_true: np.ndarray,
            y_pred: np.ndarray,
            model_name: str = "Model"
    ):
        """
        Print detailed classification report.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
        """
        print(f"\n{model_name} - Classification Report:")
        print("=" * 60)
        print(classification_report(
            y_true, y_pred,
            target_names=['Loss (0)', 'Win (1)'],
            zero_division=0
        ))

    def plot_confusion_matrix(
            self,
            y_true: np.ndarray,
            y_pred: np.ndarray,
            model_name: str = "Model",
            save_path: Optional[str] = None
    ):
        """
        Plot confusion matrix.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
            save_path: Path to save plot (optional)
        """
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Loss (0)', 'Win (1)'],
            yticklabels=['Loss (0)', 'Win (1)']
        )
        plt.title(f'{model_name} - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved confusion matrix to {save_path}")

        plt.tight_layout()
        plt.show()

    def plot_roc_curve(
            self,
            y_true: np.ndarray,
            y_pred_proba: np.ndarray,
            model_name: str = "Model",
            save_path: Optional[str] = None
    ):
        """
        Plot ROC curve.

        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            model_name: Name of the model
            save_path: Path to save plot (optional)
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        auc = roc_auc_score(y_true, y_pred_proba)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'{model_name} - ROC Curve')
        plt.legend()
        plt.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved ROC curve to {save_path}")

        plt.tight_layout()
        plt.show()

    def compare_models(
            self,
            results: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Compare multiple models.

        Args:
            results: Dictionary of {model_name: metrics_dict}

        Returns:
            DataFrame with comparison
        """
        df = pd.DataFrame(results).T

        # Sort by F1 score (or ROC-AUC if available)
        sort_by = 'roc_auc' if 'roc_auc' in df.columns else 'f1'
        df = df.sort_values(sort_by, ascending=False)

        print("\n" + "=" * 80)
        print("MODEL COMPARISON")
        print("=" * 80)
        print(df.to_string())
        print("=" * 80)

        return df