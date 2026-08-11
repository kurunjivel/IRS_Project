"""
Model Evaluator — IRS Phase 5.

Evaluates a trained model pipeline on the held-out test set and
returns a comprehensive EvaluationReport.

Metrics computed
----------------
- Accuracy
- Precision (macro + per-class)
- Recall    (macro + per-class)
- F1        (macro + per-class)
- ROC-AUC
- Confusion Matrix

Usage
-----
>>> from services.ml.model_trainer import ModelTrainer
>>> from services.ml.model_evaluator import ModelEvaluator
>>>
>>> report = ModelTrainer().train()
>>> evaluator = ModelEvaluator()
>>> eval_report = evaluator.evaluate(report.all_results[0].pipeline, report.split)
>>> print(eval_report.summary())
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from services.ml.data_preprocessor import SplitDataset

logger = logging.getLogger(__name__)


@dataclass
class EvaluationReport:
    """
    Full evaluation results for a single model on the test set.

    Attributes:
        model_name:       Classifier class name.
        accuracy:         Test-set accuracy.
        precision_macro:  Macro-averaged precision.
        recall_macro:     Macro-averaged recall.
        f1_macro:         Macro-averaged F1.
        roc_auc:          ROC-AUC score.
        confusion_matrix: 2×2 numpy array [[TN, FP], [FN, TP]].
        class_report:     Full sklearn classification_report string.
        y_pred:           Predicted labels (numpy array).
        y_proba:          Predicted probabilities for class 1 (numpy array).
    """

    model_name: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    roc_auc: float
    confusion_matrix: np.ndarray
    class_report: str
    y_pred: np.ndarray
    y_proba: np.ndarray

    def summary(self) -> str:
        """Return a human-readable evaluation summary."""
        cm = self.confusion_matrix
        tn, fp, fn, tp = cm.ravel()
        lines = [
            f"Model          : {self.model_name}",
            f"Accuracy       : {self.accuracy:.4f}",
            f"Precision(mac) : {self.precision_macro:.4f}",
            f"Recall(mac)    : {self.recall_macro:.4f}",
            f"F1(macro)      : {self.f1_macro:.4f}",
            f"ROC-AUC        : {self.roc_auc:.4f}",
            "",
            "Confusion Matrix:",
            f"  TN={tn}  FP={fp}",
            f"  FN={fn}  TP={tp}",
            "",
            "Classification Report:",
            self.class_report,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return scalar metrics as a plain dict (no arrays)."""
        return {
            "model_name": self.model_name,
            "accuracy": round(self.accuracy, 6),
            "precision_macro": round(self.precision_macro, 6),
            "recall_macro": round(self.recall_macro, 6),
            "f1_macro": round(self.f1_macro, 6),
            "roc_auc": round(self.roc_auc, 6),
        }


class ModelEvaluator:
    """
    Evaluates a fitted sklearn Pipeline on a held-out test split.

    This class is stateless — instantiate once and call evaluate()
    for each model you want to assess.
    """

    def evaluate(
        self,
        pipeline: Pipeline,
        split: SplitDataset,
    ) -> EvaluationReport:
        """
        Evaluate a fitted pipeline on the test split.

        Args:
            pipeline: A fitted sklearn Pipeline (scaler + classifier).
            split:    SplitDataset from DataPreprocessor.load_and_split().

        Returns:
            EvaluationReport with all metrics populated.
        """
        model_name = type(pipeline.named_steps["clf"]).__name__

        y_pred = pipeline.predict(split.X_test)
        y_proba = self._predict_proba(pipeline, split.X_test)

        accuracy = float(accuracy_score(split.y_test, y_pred))
        precision = float(precision_score(split.y_test, y_pred, average="macro", zero_division=0))
        recall = float(recall_score(split.y_test, y_pred, average="macro", zero_division=0))
        f1 = float(f1_score(split.y_test, y_pred, average="macro", zero_division=0))
        roc_auc = float(roc_auc_score(split.y_test, y_proba))
        cm = confusion_matrix(split.y_test, y_pred)
        report = classification_report(
            split.y_test, y_pred,
            target_names=["Not Promoted", "Promoted"],
            zero_division=0,
        )

        logger.info(
            "%s — Accuracy=%.4f, F1=%.4f, ROC-AUC=%.4f",
            model_name, accuracy, f1, roc_auc,
        )

        return EvaluationReport(
            model_name=model_name,
            accuracy=accuracy,
            precision_macro=precision,
            recall_macro=recall,
            f1_macro=f1,
            roc_auc=roc_auc,
            confusion_matrix=cm,
            class_report=report,
            y_pred=y_pred,
            y_proba=y_proba,
        )

    def evaluate_all(
        self,
        pipelines: list[tuple[str, Pipeline]],
        split: SplitDataset,
    ) -> list[EvaluationReport]:
        """
        Evaluate multiple pipelines and return sorted results (best F1 first).

        Args:
            pipelines: List of (name, fitted_pipeline) tuples.
            split:     SplitDataset from DataPreprocessor.load_and_split().

        Returns:
            List of EvaluationReport sorted by f1_macro descending.
        """
        reports = [self.evaluate(pipeline, split) for _, pipeline in pipelines]
        return sorted(reports, key=lambda r: r.f1_macro, reverse=True)

    def comparison_dataframe(self, reports: list[EvaluationReport]) -> pd.DataFrame:
        """
        Build a comparison DataFrame from a list of EvaluationReports.

        Args:
            reports: List of EvaluationReport objects.

        Returns:
            DataFrame with one row per model, sorted by F1 descending.
        """
        rows = [r.to_dict() for r in reports]
        df = pd.DataFrame(rows).sort_values("f1_macro", ascending=False)
        df = df.rename(columns={
            "model_name": "Model",
            "accuracy": "Accuracy",
            "precision_macro": "Precision",
            "recall_macro": "Recall",
            "f1_macro": "F1 (macro)",
            "roc_auc": "ROC-AUC",
        })
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _predict_proba(pipeline: Pipeline, X: pd.DataFrame) -> np.ndarray:
        """
        Return probability estimates for class 1.

        Falls back to decision_function (normalised) if predict_proba
        is not available (e.g. LinearSVC).
        """
        clf = pipeline.named_steps["clf"]
        if hasattr(clf, "predict_proba"):
            return pipeline.predict_proba(X)[:, 1]
        # Fallback: use decision_function and apply sigmoid
        scores = pipeline.decision_function(X)
        return 1.0 / (1.0 + np.exp(-scores))
