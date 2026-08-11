"""
Predictor — IRS Phase 5.

Loads the saved promotion model and produces structured predictions
for individual employees or batches.

Prediction output schema
------------------------
{
    "employee_id":           int,
    "current_grade":         str,   e.g. "G2"
    "target_grade":          str,   e.g. "G3"
    "promotion_probability": float, e.g. 0.87
    "prediction":            str,   "Likely Progression" | "Unlikely Progression"
    "model_name":            str,   e.g. "RandomForestClassifier"
}

Threshold
---------
Default decision threshold is 0.50.  A custom threshold can be passed
to predict() to tune precision/recall trade-off.

Usage
-----
>>> predictor = Predictor()
>>> result = predictor.predict(feature_row, employee_id=101,
...                            current_grade="G2", target_grade="G3")
>>> print(result)
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path

import pandas as pd

from services.ml.feature_engineering import FEATURE_COLUMNS
from services.ml.model_trainer import METADATA_PATH, MODEL_PATH

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prediction labels
# ---------------------------------------------------------------------------
LABEL_POSITIVE: str = "Likely Progression"
LABEL_NEGATIVE: str = "Unlikely Progression"
DEFAULT_THRESHOLD: float = 0.50


class Predictor:
    """
    Loads the saved promotion model and generates predictions.

    The model is loaded lazily on first use and cached for subsequent
    calls.  Call reload() to force a fresh load from disk.

    Parameters
    ----------
    model_path    : Path to the .pkl model file.
    metadata_path : Path to the model_metadata.json file.
    threshold     : Decision threshold for positive class (default 0.50).
    """

    def __init__(
        self,
        model_path: Path | str | None = None,
        metadata_path: Path | str | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self._model_path = Path(model_path) if model_path else MODEL_PATH
        self._metadata_path = Path(metadata_path) if metadata_path else METADATA_PATH
        self._threshold = threshold
        self._pipeline = None
        self._metadata: dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(
        self,
        features: dict | pd.Series | pd.DataFrame,
        employee_id: int = 0,
        current_grade: str = "",
        target_grade: str = "",
    ) -> dict:
        """
        Predict promotion likelihood for a single employee.

        Args:
            features:      Feature dict, Series, or single-row DataFrame.
                           Must contain all FEATURE_COLUMNS keys.
            employee_id:   Employee identifier (for traceability).
            current_grade: Current grade string, e.g. "G2".
            target_grade:  Target grade string, e.g. "G3".

        Returns:
            Prediction dict with the required output schema.

        Raises:
            FileNotFoundError: If the model file does not exist.
            ValueError:        If required features are missing.
        """
        pipeline = self._load_pipeline()
        X = self._to_dataframe(features)
        self._validate_features(X)

        proba = float(pipeline.predict_proba(X)[0, 1])
        label = LABEL_POSITIVE if proba >= self._threshold else LABEL_NEGATIVE

        result = {
            "employee_id": int(employee_id),
            "current_grade": str(current_grade),
            "target_grade": str(target_grade),
            "promotion_probability": round(proba, 4),
            "prediction": label,
            "model_name": self.model_name,
        }
        logger.debug(
            "Prediction for employee %d: %s (p=%.4f)",
            employee_id, label, proba,
        )
        return result

    def predict_batch(
        self,
        df: pd.DataFrame,
        employee_ids: list[int] | None = None,
        current_grades: list[str] | None = None,
        target_grades: list[str] | None = None,
    ) -> list[dict]:
        """
        Predict promotion likelihood for a batch of employees.

        Args:
            df:             DataFrame with FEATURE_COLUMNS columns.
            employee_ids:   Optional list of employee IDs (same length as df).
            current_grades: Optional list of current grade strings.
            target_grades:  Optional list of target grade strings.

        Returns:
            List of prediction dicts, one per row.
        """
        pipeline = self._load_pipeline()
        self._validate_features(df)

        n = len(df)
        ids = employee_ids or [0] * n
        cur = current_grades or [""] * n
        tgt = target_grades or [""] * n

        probas = pipeline.predict_proba(df[FEATURE_COLUMNS])[:, 1]
        results = []
        for i, proba in enumerate(probas):
            label = LABEL_POSITIVE if proba >= self._threshold else LABEL_NEGATIVE
            results.append({
                "employee_id": int(ids[i]),
                "current_grade": str(cur[i]),
                "target_grade": str(tgt[i]),
                "promotion_probability": round(float(proba), 4),
                "prediction": label,
                "model_name": self.model_name,
            })
        return results

    def reload(self) -> None:
        """Force reload of the model and metadata from disk."""
        self._pipeline = None
        self._metadata = {}
        self._load_pipeline()
        logger.info("Model reloaded from %s.", self._model_path)

    @property
    def model_name(self) -> str:
        """Name of the loaded classifier."""
        self._load_pipeline()
        return self._metadata.get("model_name", "Unknown")

    @property
    def feature_columns(self) -> list[str]:
        """Ordered feature columns expected by the model."""
        self._load_pipeline()
        return self._metadata.get("feature_columns", FEATURE_COLUMNS)

    @property
    def threshold(self) -> float:
        """Current decision threshold."""
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        if not 0.0 < value < 1.0:
            raise ValueError(f"Threshold must be in (0, 1), got {value}.")
        self._threshold = value

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_pipeline(self):
        """Lazy-load the model pipeline from disk."""
        if self._pipeline is not None:
            return self._pipeline

        if not self._model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self._model_path}. "
                "Run ModelTrainer().train() first."
            )

        with self._model_path.open("rb") as fh:
            self._pipeline = pickle.load(fh)

        if self._metadata_path.exists():
            with self._metadata_path.open("r", encoding="utf-8") as fh:
                self._metadata = json.load(fh)

        logger.info(
            "Model loaded: %s from %s.",
            self._metadata.get("model_name", "?"), self._model_path,
        )
        return self._pipeline

    @staticmethod
    def _to_dataframe(features: dict | pd.Series | pd.DataFrame) -> pd.DataFrame:
        """Normalise input to a single-row DataFrame."""
        if isinstance(features, pd.DataFrame):
            return features.reset_index(drop=True)
        if isinstance(features, pd.Series):
            return features.to_frame().T.reset_index(drop=True)
        if isinstance(features, dict):
            return pd.DataFrame([features])
        raise TypeError(
            f"features must be dict, pd.Series, or pd.DataFrame, got {type(features)}."
        )

    def _validate_features(self, df: pd.DataFrame) -> None:
        """Raise ValueError if any required feature column is missing."""
        expected = self.feature_columns
        missing = [c for c in expected if c not in df.columns]
        if missing:
            raise ValueError(
                f"Missing feature columns: {missing}. "
                f"Expected all of: {expected}"
            )
