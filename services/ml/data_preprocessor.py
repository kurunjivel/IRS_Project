"""
Data Preprocessor — IRS Phase 4.

Loads the saved dataset, applies preprocessing, and returns
ML-ready (X_train, X_test, y_train, y_test) splits.

Responsibilities
----------------
- Load dataset from CSV.
- Separate features (X) and target (y).
- Encode categorical features (grade columns are already ordinal integers;
  no string categories remain after DatasetGenerator).
- Handle missing values (log and impute with column median).
- Remove duplicate rows (log count removed).
- Validate numeric ranges and clip outliers.
- Perform 80/20 stratified train/test split.

This file does NOT train any model.

Train/test split
----------------
    Training set : 80 %
    Test set     : 20 %
    stratify=y   : preserves class distribution in both splits
    random_state : 42
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from services.ml.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN
from services.ml.dataset_generator import DEFAULT_OUTPUT_PATH

logger = logging.getLogger(__name__)

RANDOM_STATE: int = 42
TEST_SIZE: float = 0.20


@dataclass
class SplitDataset:
    """
    Container for the preprocessed train/test split.

    Attributes:
        X_train: Training feature matrix.
        X_test:  Test feature matrix.
        y_train: Training target vector.
        y_test:  Test target vector.
        feature_columns: Ordered list of feature column names.
    """

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_columns: list[str]

    @property
    def train_rows(self) -> int:
        return len(self.X_train)

    @property
    def test_rows(self) -> int:
        return len(self.X_test)

    @property
    def total_rows(self) -> int:
        return self.train_rows + self.test_rows

    def summary(self) -> str:
        """Return a human-readable summary string."""
        pos_train = int(self.y_train.sum())
        pos_test  = int(self.y_test.sum())
        return (
            f"Total rows  : {self.total_rows}\n"
            f"Train rows  : {self.train_rows}  "
            f"(positive={pos_train}, negative={self.train_rows - pos_train})\n"
            f"Test rows   : {self.test_rows}  "
            f"(positive={pos_test}, negative={self.test_rows - pos_test})\n"
            f"Features    : {len(self.feature_columns)}\n"
        )


class DataPreprocessor:
    """
    Loads and preprocesses the Phase 4 dataset for ML training.

    Parameters
    ----------
    dataset_path : Path to the CSV file.  Defaults to
                   datasets/historical_employee_progression.csv.
    """

    def __init__(self, dataset_path: Path | str | None = None) -> None:
        self._path = Path(dataset_path) if dataset_path else DEFAULT_OUTPUT_PATH

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_and_split(self) -> SplitDataset:
        """
        Full preprocessing pipeline: load → clean → split.

        Returns:
            SplitDataset with X_train, X_test, y_train, y_test.

        Raises:
            FileNotFoundError: If the dataset CSV does not exist.
            ValueError: If the dataset has no usable rows after cleaning.
        """
        df = self._load()
        df = self._remove_duplicates(df)
        df = self._handle_missing(df)
        df = self._clip_ranges(df)
        X, y = self._separate(df)
        return self._split(X, y)

    def load_raw(self) -> pd.DataFrame:
        """
        Load the raw CSV without any preprocessing.

        Returns:
            Full DataFrame including TARGET_COLUMN.
        """
        return self._load()

    # ------------------------------------------------------------------
    # Private pipeline steps
    # ------------------------------------------------------------------

    def _load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self._path}. "
                "Run DatasetGenerator.save() first."
            )
        df = pd.read_csv(self._path, comment="#")
        logger.info("Loaded %d rows from %s.", len(df), self._path)
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        if removed:
            logger.warning("Removed %d duplicate row(s).", removed)
        else:
            logger.info("No duplicate rows found.")
        return df

    def _handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values with the column median.
        Logs each column that required imputation.
        """
        all_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
        for col in all_cols:
            if col not in df.columns:
                continue
            n_missing = df[col].isnull().sum()
            if n_missing > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                logger.warning(
                    "Imputed %d missing value(s) in '%s' with median=%.4f.",
                    n_missing, col, median_val,
                )
        return df

    def _clip_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clip numeric features to valid ranges."""
        _rules: list[tuple[str, float, float]] = [
            ("experience_years",              0.0,  50.0),
            ("performance_rating",            1.0,   5.0),
            ("current_grade_encoded",         1.0,   5.0),
            ("target_grade_encoded",          1.0,   5.0),
            ("skill_coverage_percentage",     0.0, 100.0),
            ("average_skill_level",           0.0,   5.0),
            ("certification_completion_rate", 0.0,   1.0),
            ("project_completion_rate",       0.0,   1.0),
            ("lead_project_completion_rate",  0.0,   1.0),
            ("average_project_rating",        0.0,   5.0),
            ("readiness_score",               0.0, 100.0),
            ("skill_score",                   0.0,  40.0),
            ("certification_score",           0.0,  15.0),
            ("experience_score",              0.0,  15.0),
            ("project_score",                 0.0,  20.0),
            ("performance_score",             0.0,  10.0),
        ]
        for col, lo, hi in _rules:
            if col in df.columns:
                df[col] = df[col].clip(lower=lo, upper=hi)
        return df

    def _separate(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Split into feature matrix X and target vector y."""
        missing_feat = [c for c in FEATURE_COLUMNS if c not in df.columns]
        if missing_feat:
            raise ValueError(f"Missing feature columns: {missing_feat}")
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")

        X = df[FEATURE_COLUMNS].copy()
        y = df[TARGET_COLUMN].astype(int)
        return X, y

    def _split(
        self, X: pd.DataFrame, y: pd.Series
    ) -> SplitDataset:
        """
        80/20 stratified train/test split.

        Uses stratify=y to preserve class distribution.
        Falls back to non-stratified split if class distribution
        prevents stratification (e.g. very small datasets).
        """
        if len(X) == 0:
            raise ValueError("Dataset has no usable rows after preprocessing.")

        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=TEST_SIZE,
                random_state=RANDOM_STATE,
                stratify=y,
            )
            logger.info(
                "Stratified split: train=%d, test=%d.", len(X_train), len(X_test)
            )
        except ValueError:
            logger.warning(
                "Stratified split failed (class imbalance?). "
                "Falling back to non-stratified split."
            )
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=TEST_SIZE,
                random_state=RANDOM_STATE,
            )

        return SplitDataset(
            X_train=X_train.reset_index(drop=True),
            X_test=X_test.reset_index(drop=True),
            y_train=y_train.reset_index(drop=True),
            y_test=y_test.reset_index(drop=True),
            feature_columns=FEATURE_COLUMNS,
        )
