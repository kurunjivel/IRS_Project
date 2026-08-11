"""
Model Trainer — IRS Phase 5.

Trains and compares multiple classifiers on the Phase 4 dataset,
selects the best model based on cross-validated F1 score (not accuracy
alone), and persists the winner to ml_models/promotion_model.pkl.

Models trained
--------------
1. LogisticRegression   — linear baseline, interpretable
2. DecisionTreeClassifier — non-linear, human-readable rules
3. RandomForestClassifier — ensemble, robust to noise

XGBoost is included only when the ``xgboost`` package is installed.

Model selection
---------------
Best model is chosen by mean cross-validated F1 (macro) on the training
set.  F1 is preferred over accuracy because the dataset has a class
imbalance (~72 % promoted).

Persistence
-----------
The winning model pipeline (scaler + classifier) is saved as:
    ml_models/promotion_model.pkl

A companion metadata file is saved as:
    ml_models/model_metadata.json

Both files are required by Predictor.
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from services.ml.data_preprocessor import DataPreprocessor, SplitDataset
from services.ml.feature_engineering import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR: Path = _PROJECT_ROOT / "ml_models"
MODEL_PATH: Path = MODEL_DIR / "promotion_model.pkl"
METADATA_PATH: Path = MODEL_DIR / "model_metadata.json"

# ---------------------------------------------------------------------------
# Cross-validation config
# ---------------------------------------------------------------------------
CV_FOLDS: int = 5
RANDOM_STATE: int = 42


@dataclass
class ModelResult:
    """
    Holds training results for a single candidate model.

    Attributes:
        name:          Classifier class name.
        pipeline:      Fitted sklearn Pipeline (scaler + classifier).
        cv_scores:     Dict of cross-validation metric arrays.
        mean_f1:       Mean CV F1 (macro) — primary selection criterion.
        mean_accuracy: Mean CV accuracy.
        mean_roc_auc:  Mean CV ROC-AUC.
    """

    name: str
    pipeline: Pipeline
    cv_scores: dict[str, np.ndarray]
    mean_f1: float
    mean_accuracy: float
    mean_roc_auc: float
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingReport:
    """
    Summary of the full training run.

    Attributes:
        best_model_name: Name of the selected model.
        all_results:     List of ModelResult for every candidate.
        model_path:      Path where the best model was saved.
        feature_columns: Ordered feature column list used during training.
        split:           The SplitDataset used for training.
    """

    best_model_name: str
    all_results: list[ModelResult]
    model_path: Path
    feature_columns: list[str]
    split: SplitDataset

    def comparison_table(self) -> pd.DataFrame:
        """Return a DataFrame comparing all candidate models."""
        rows = [
            {
                "Model": r.name,
                "CV F1 (macro)": round(r.mean_f1, 4),
                "CV Accuracy": round(r.mean_accuracy, 4),
                "CV ROC-AUC": round(r.mean_roc_auc, 4),
                "Selected": "✓" if r.name == self.best_model_name else "",
            }
            for r in self.all_results
        ]
        return pd.DataFrame(rows).sort_values("CV F1 (macro)", ascending=False)


class ModelTrainer:
    """
    Trains, compares, and persists promotion prediction models.

    Parameters
    ----------
    dataset_path : Optional path to the CSV dataset.  Defaults to
                   datasets/historical_employee_progression.csv.
    model_dir    : Directory to save the trained model.  Defaults to
                   ml_models/.
    """

    def __init__(
        self,
        dataset_path: Path | str | None = None,
        model_dir: Path | str | None = None,
    ) -> None:
        self._preprocessor = DataPreprocessor(dataset_path)
        self._model_dir = Path(model_dir) if model_dir else MODEL_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(self) -> TrainingReport:
        """
        Full training pipeline: load → split → train → compare → save.

        Returns:
            TrainingReport with best model name, all results, and paths.
        """
        split = self._preprocessor.load_and_split()
        logger.info(
            "Training on %d samples, testing on %d samples.",
            split.train_rows, split.test_rows,
        )

        candidates = self._build_candidates()
        results: list[ModelResult] = []

        for name, pipeline, params in candidates:
            result = self._cross_validate(name, pipeline, params, split)
            results.append(result)
            logger.info(
                "%s — CV F1=%.4f, Accuracy=%.4f, ROC-AUC=%.4f",
                name, result.mean_f1, result.mean_accuracy, result.mean_roc_auc,
            )

        # Select best by F1 (macro), break ties by ROC-AUC
        best = max(results, key=lambda r: (r.mean_f1, r.mean_roc_auc))
        logger.info("Best model: %s (CV F1=%.4f)", best.name, best.mean_f1)

        # Refit best model on full training set
        best.pipeline.fit(split.X_train, split.y_train)

        model_path = self._save(best, split.feature_columns)

        return TrainingReport(
            best_model_name=best.name,
            all_results=results,
            model_path=model_path,
            feature_columns=split.feature_columns,
            split=split,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_candidates(
        self,
    ) -> list[tuple[str, Pipeline, dict]]:
        """Return list of (name, unfitted_pipeline, params) tuples."""
        candidates = [
            (
                "LogisticRegression",
                Pipeline([
                    ("scaler", StandardScaler()),
                    ("clf", LogisticRegression(
                        max_iter=1000,
                        random_state=RANDOM_STATE,
                        class_weight="balanced",
                    )),
                ]),
                {"max_iter": 1000, "class_weight": "balanced"},
            ),
            (
                "DecisionTreeClassifier",
                Pipeline([
                    ("scaler", StandardScaler()),
                    ("clf", DecisionTreeClassifier(
                        max_depth=8,
                        min_samples_leaf=10,
                        random_state=RANDOM_STATE,
                        class_weight="balanced",
                    )),
                ]),
                {"max_depth": 8, "min_samples_leaf": 10, "class_weight": "balanced"},
            ),
            (
                "RandomForestClassifier",
                Pipeline([
                    ("scaler", StandardScaler()),
                    ("clf", RandomForestClassifier(
                        n_estimators=200,
                        max_depth=10,
                        min_samples_leaf=5,
                        random_state=RANDOM_STATE,
                        class_weight="balanced",
                        n_jobs=-1,
                    )),
                ]),
                {
                    "n_estimators": 200,
                    "max_depth": 10,
                    "min_samples_leaf": 5,
                    "class_weight": "balanced",
                },
            ),
        ]

        # Include XGBoost only if installed
        try:
            from xgboost import XGBClassifier  # type: ignore
            candidates.append((
                "XGBClassifier",
                Pipeline([
                    ("scaler", StandardScaler()),
                    ("clf", XGBClassifier(
                        n_estimators=200,
                        max_depth=6,
                        learning_rate=0.1,
                        random_state=RANDOM_STATE,
                        eval_metric="logloss",
                        use_label_encoder=False,
                    )),
                ]),
                {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1},
            ))
            logger.info("XGBoost detected — added as candidate.")
        except ImportError:
            logger.info("XGBoost not installed — skipping.")

        return candidates

    def _cross_validate(
        self,
        name: str,
        pipeline: Pipeline,
        params: dict,
        split: SplitDataset,
    ) -> ModelResult:
        """Run stratified k-fold CV and return a ModelResult."""
        cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_validate(
            pipeline,
            split.X_train,
            split.y_train,
            cv=cv,
            scoring=["accuracy", "f1_macro", "roc_auc"],
            return_train_score=False,
            n_jobs=-1,
        )
        return ModelResult(
            name=name,
            pipeline=pipeline,
            cv_scores=scores,
            mean_f1=float(scores["test_f1_macro"].mean()),
            mean_accuracy=float(scores["test_accuracy"].mean()),
            mean_roc_auc=float(scores["test_roc_auc"].mean()),
            params=params,
        )

    def _save(self, result: ModelResult, feature_columns: list[str]) -> Path:
        """Persist the fitted pipeline and metadata."""
        self._model_dir.mkdir(parents=True, exist_ok=True)

        model_path = self._model_dir / "promotion_model.pkl"
        with model_path.open("wb") as fh:
            pickle.dump(result.pipeline, fh)
        logger.info("Model saved to %s.", model_path)

        metadata = {
            "model_name": result.name,
            "feature_columns": feature_columns,
            "cv_f1_macro": round(result.mean_f1, 6),
            "cv_accuracy": round(result.mean_accuracy, 6),
            "cv_roc_auc": round(result.mean_roc_auc, 6),
            "cv_folds": CV_FOLDS,
            "random_state": RANDOM_STATE,
            "params": result.params,
        }
        metadata_path = self._model_dir / "model_metadata.json"
        with metadata_path.open("w", encoding="utf-8") as fh:
            json.dump(metadata, fh, indent=2)
        logger.info("Metadata saved to %s.", metadata_path)

        return model_path
