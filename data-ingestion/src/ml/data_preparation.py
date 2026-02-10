"""Data preparation for ML models."""
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class DataPreparation:
    """Prepare data for ML models."""

    def __init__(self):
        """Initialize data preparation."""
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_column = 'target_win'

    def load_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load feature data from CSV.

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with features
        """
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df

    def filter_complete_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter to only runners with known outcomes.

        Args:
            df: Full DataFrame

        Returns:
            DataFrame with only complete data (target_win >= 0)
        """
        # Remove rows without results (target_win = -1)
        complete_df = df[df['target_win'] >= 0].copy()

        logger.info(f"Filtered to {len(complete_df)} runners with results")
        logger.info(f"  Wins: {(complete_df['target_win'] == 1).sum()}")
        logger.info(f"  Losses: {(complete_df['target_win'] == 0).sum()}")

        return complete_df

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (exclude IDs and targets).

        Args:
            df: DataFrame

        Returns:
            List of feature column names
        """
        # Columns to exclude
        exclude_cols = [
            'runner_id', 'race_id', 'meet_id',
            'target_win', 'target_finish_position'
        ]

        # Get all numeric columns except excluded ones
        feature_cols = [
            col for col in df.columns
            if col not in exclude_cols and df[col].dtype in ['float64', 'int64']
        ]

        logger.info(f"Selected {len(feature_cols)} feature columns")
        return feature_cols

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in features.

        Args:
            df: DataFrame

        Returns:
            DataFrame with missing values handled
        """
        # Fill numeric missing values with median
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                logger.info(f"Filled {col} missing values with median: {median_val:.4f}")

        return df

    def time_based_split(
            self,
            df: pd.DataFrame,
            train_ratio: float = 0.8
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data by time to prevent data leakage.

        CRITICAL: In horse racing, we must use time-based splits!
        Cannot use random splits because future races use past performance.

        Args:
            df: DataFrame with race data
            train_ratio: Proportion for training (default 0.8)

        Returns:
            Tuple of (train_df, test_df)
        """
        # Sort by race_id (which is chronological from database)
        df_sorted = df.sort_values('race_id').reset_index(drop=True)

        # Calculate split point
        split_idx = int(len(df_sorted) * train_ratio)

        train_df = df_sorted.iloc[:split_idx].copy()
        test_df = df_sorted.iloc[split_idx:].copy()

        logger.info(f"Time-based split:")
        logger.info(f"  Training set: {len(train_df)} runners")
        logger.info(f"  Test set: {len(test_df)} runners")
        logger.info(
            f"  Train wins: {(train_df['target_win'] == 1).sum()} ({(train_df['target_win'] == 1).sum() / len(train_df) * 100:.1f}%)")
        logger.info(
            f"  Test wins: {(test_df['target_win'] == 1).sum()} ({(test_df['target_win'] == 1).sum() / len(test_df) * 100:.1f}%)")

        return train_df, test_df

    def prepare_features_and_target(
            self,
            df: pd.DataFrame,
            feature_columns: List[str]
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Separate features and target.

        Args:
            df: DataFrame
            feature_columns: List of feature column names

        Returns:
            Tuple of (X, y)
        """
        X = df[feature_columns].copy()
        y = df['target_win'].copy()

        return X, y

    def scale_features(
            self,
            X_train: pd.DataFrame,
            X_test: pd.DataFrame,
            fit: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Scale features using StandardScaler.

        Args:
            X_train: Training features
            X_test: Test features
            fit: Whether to fit the scaler (True for first time)

        Returns:
            Tuple of (X_train_scaled, X_test_scaled)
        """
        if fit:
            # Fit on training data only
            self.scaler.fit(X_train)
            logger.info("Fitted scaler on training data")

        # Transform both sets
        X_train_scaled = pd.DataFrame(
            self.scaler.transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )

        X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )

        logger.info("Scaled features")
        return X_train_scaled, X_test_scaled

    def prepare_ml_data(
            self,
            filepath: Path,
            train_ratio: float = 0.8,
            scale: bool = True
    ) -> dict:
        """
        Complete data preparation pipeline.

        Args:
            filepath: Path to feature CSV
            train_ratio: Train/test split ratio
            scale: Whether to scale features

        Returns:
            Dictionary with prepared data:
            {
                'X_train': Training features,
                'X_test': Test features,
                'y_train': Training targets,
                'y_test': Test targets,
                'feature_columns': List of feature names
            }
        """
        # Load data
        df = self.load_data(filepath)

        # Filter to complete data only
        df = self.filter_complete_data(df)

        # Handle missing values
        df = self.handle_missing_values(df)

        # Get feature columns
        feature_columns = self.get_feature_columns(df)
        self.feature_columns = feature_columns

        # Time-based split
        train_df, test_df = self.time_based_split(df, train_ratio)

        # Prepare features and target
        X_train, y_train = self.prepare_features_and_target(train_df, feature_columns)
        X_test, y_test = self.prepare_features_and_target(test_df, feature_columns)

        # Scale features
        if scale:
            X_train, X_test = self.scale_features(X_train, X_test, fit=True)

        logger.info(f"Data preparation complete")
        logger.info(f"  Features: {len(feature_columns)}")
        logger.info(f"  Training samples: {len(X_train)}")
        logger.info(f"  Test samples: {len(X_test)}")

        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'feature_columns': feature_columns
        }