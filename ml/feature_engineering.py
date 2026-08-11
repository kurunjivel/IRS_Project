"""
Feature Engineering — IRS Phase 4.

Extracts a flat, ML-ready feature vector from the combined output of
Phase 2 (gap analysis) and Phase 3 (readiness scoring).

This module is the bridge between the rule-based pipeline and the ML model.
It is used in two contexts:

1. At training time — to convert synthetic (or future real) records into
   the feature matrix that the model is trained on.

2. At inference time — to convert a live employee's Phase 2 + Phase 3
   output into the same feature vector so the trained model can predict
   their promotion probability.

The feature set is intentionally restricted to job-relevant factors.
No protected or sensitive personal attributes are included.

Feature vector (18 features, in order)
---------------------------------------
 0  experience_years
 1  performance_rating
 2  skill_coverage_pct
 3  avg_skill_level
 4  mandatory_skill_gap_count
 5  cert_completion_rate
 6  project_completion_rate
 7  lead_project_completion_rate
 8  avg_project_rating
 9  current_grade_encoded
10  target_grade_encoded
11  grade_gap
12  skill_score
13  cert_score
14  experience_score
15  project_score
16  performance_score
17  readiness_score
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ordered feature names — single source of truth used by training and inference
# ---------------------------------------------------------------------------

FEATURE_NAMES: list[str] = [
    "experience_years",
    "performance_rating",
    "skill_coverage_pct",
    "avg_skill_level",
    "mandatory_skill_gap_count",
    "cert_completion_rate",
    "project_completion_rate",
    "lead_project_completion_rate",
    "avg_project_rating",
    "current_grade_encoded",
    "target_grade_encoded",
    "grade_gap",
    "skill_score",
    "cert_score",
    "experience_score",
    "project_score",
    "performance_score",
    "readiness_score",
]

TARGET_COLUMN: str = "promotion_success"

# Grade ordinal encoding — must match SyntheticDatasetGenerator._GRADE_TO_INT.
_GRADE_TO_INT: dict[str, int] = {
    "G1": 1, "G2": 2, "G3": 3, "G4": 4, "G5": 5,
}

# Phase 3 scoring maxima — kept in sync with Phase 3 service constants.
_SKILL_MAX: float = 40.0
_CERT_MAX: float = 15.0
_EXP_MAX: float = 15.0
_PROJ_MAX: float = 20.0
_PERF_MAX: float = 10.0


@dataclass
class FeatureVector:
    """
    A single employee's ML feature vector.

    Attributes:
        features:      Ordered dict mapping feature name → value.
        employee_id:   Source employee ID (for traceability).
        feature_names: Ordered list of feature names (same as FEATURE_NAMES).
    """

    features: dict[str, float]
    employee_id: int
    feature_names: list[str]

    def to_numpy(self) -> np.ndarray:
        """Return features as a 1-D NumPy array in FEATURE_NAMES order."""
        return np.array([self.features[f] for f in self.feature_names], dtype=np.float64)

    def to_dataframe(self) -> pd.DataFrame:
        """Return features as a single-row DataFrame with correct column names."""
        return pd.DataFrame([self.features], columns=self.feature_names)


class FeatureEngineer:
    """
    Extracts a flat ML feature vector from Phase 2 + Phase 3 pipeline output.

    This class is stateless — it holds no mutable state and can be reused
    across multiple employees without re-instantiation.

    Usage (inference)
    -----------------
    >>> engineer = FeatureEngineer()
    >>> fv = engineer.extract(gap_analysis, readiness_result)
    >>> X  = fv.to_numpy().reshape(1, -1)   # ready for model.predict_proba(X)
    """

    def extract(
        self,
        gap_analysis: dict,
        readiness_result,
    ) -> FeatureVector:
        """
        Extract the feature vector for a single employee.

        Args:
            gap_analysis:     The dict returned by GapAnalysisService.run().
                              Must contain keys: employee, requirement,
                              skill_gaps, certification_gaps,
                              experience_gap, project_gap.
            readiness_result: The ReadinessResult returned by
                              ReadinessEngine.calculate().

        Returns:
            FeatureVector with all 18 features populated.
        """
        employee: Employee = gap_analysis["employee"]
        requirement: GradeRequirement = gap_analysis["requirement"]
        skill_gaps: list[dict] = gap_analysis["skill_gaps"]
        cert_gaps: list[dict] = gap_analysis["certification_gaps"]
        exp_gap: dict = gap_analysis["experience_gap"]
        proj_gap: dict = gap_analysis["project_gap"]
        breakdown = readiness_result.breakdown

        features = {
            # --- raw job-relevant features ---
            "experience_years":             float(employee.experience_years),
            "performance_rating":           float(employee.performance_rating),
            "skill_coverage_pct":           self._skill_coverage_pct(
                                                skill_gaps, requirement
                                            ),
            "avg_skill_level":              self._avg_skill_level(employee),
            "mandatory_skill_gap_count":    self._mandatory_gap_count(skill_gaps),
            "cert_completion_rate":         self._cert_completion_rate(
                                                cert_gaps, requirement
                                            ),
            "project_completion_rate":      self._project_completion_rate(proj_gap),
            "lead_project_completion_rate": self._lead_completion_rate(proj_gap),
            "avg_project_rating":           self._avg_project_rating(employee),
            "current_grade_encoded":        float(
                                                _GRADE_TO_INT.get(
                                                    employee.current_grade, 0
                                                )
                                            ),
            "target_grade_encoded":         float(
                                                _GRADE_TO_INT.get(
                                                    employee.target_grade, 0
                                                )
                                            ),
            "grade_gap":                    self._grade_gap(employee),
            # --- Phase 3 derived scores ---
            "skill_score":                  float(breakdown.skills.score),
            "cert_score":                   float(breakdown.certifications.score),
            "experience_score":             float(breakdown.experience.score),
            "project_score":                float(breakdown.projects.score),
            "performance_score":            float(breakdown.performance.score),
            "readiness_score":              float(readiness_result.readiness_score),
        }

        logger.debug(
            "Feature vector extracted for employee %s: readiness_score=%.2f",
            employee.employee_id,
            features["readiness_score"],
        )

        return FeatureVector(
            features=features,
            employee_id=employee.employee_id,
            feature_names=FEATURE_NAMES,
        )

    # ------------------------------------------------------------------
    # Private extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _skill_coverage_pct(
        skill_gaps: list[dict],
        requirement: GradeRequirement,
    ) -> float:
        """Percentage of required skills the employee meets or exceeds."""
        total = len(requirement.skills)
        if total == 0:
            return 100.0
        gap_names = {g["skill"].lower() for g in skill_gaps}
        met = sum(
            1 for s in requirement.skills
            if s.skill_name.lower() not in gap_names
        )
        return round((met / total) * 100.0, 2)

    @staticmethod
    def _avg_skill_level(employee: Employee) -> float:
        """Mean skill level across all skills the employee holds."""
        if not employee.skills:
            return 0.0
        return round(
            sum(s.skill_level for s in employee.skills) / len(employee.skills), 2
        )

    @staticmethod
    def _mandatory_gap_count(skill_gaps: list[dict]) -> float:
        """Number of mandatory skill gaps."""
        return float(sum(1 for g in skill_gaps if g.get("mandatory", False)))

    @staticmethod
    def _cert_completion_rate(
        cert_gaps: list[dict],
        requirement: GradeRequirement,
    ) -> float:
        """Fraction of required certifications the employee has completed."""
        total = len(requirement.certifications)
        if total == 0:
            return 1.0
        missing = len(cert_gaps)
        return round((total - missing) / total, 3)

    @staticmethod
    def _project_completion_rate(proj_gap: dict) -> float:
        """Fraction of required projects completed (capped at 1.0)."""
        required = proj_gap["required_projects"]
        if required == 0:
            return 1.0
        return round(min(proj_gap["total_projects"] / required, 1.0), 3)

    @staticmethod
    def _lead_completion_rate(proj_gap: dict) -> float:
        """Fraction of required lead projects completed (capped at 1.0)."""
        required = proj_gap["required_lead_projects"]
        if required == 0:
            return 1.0
        return round(min(proj_gap["lead_projects"] / required, 1.0), 3)

    @staticmethod
    def _avg_project_rating(employee: Employee) -> float:
        """Mean project rating across all projects the employee has completed."""
        rated = [
            p.project_rating
            for p in employee.projects
            if p.project_rating is not None
        ]
        if not rated:
            return 0.0
        return round(sum(rated) / len(rated), 2)

    @staticmethod
    def _grade_gap(employee: Employee) -> float:
        """Ordinal distance between current and target grade."""
        current = _GRADE_TO_INT.get(employee.current_grade, 0)
        target = _GRADE_TO_INT.get(employee.target_grade, 0)
        return float(max(target - current, 0))


class DataFrameFeatureEngineer:
    """
    Validates and preprocesses a feature DataFrame for ML training/inference.

    Responsibilities:
    - Verify all expected columns are present.
    - Clip values to valid ranges to guard against data quality issues.
    - Return a clean, typed DataFrame ready for scikit-learn.
    """

    # (column, min_value, max_value)
    _CLIP_RULES: list[tuple[str, float, float]] = [
        ("experience_years",             0.0,   20.0),
        ("performance_rating",           1.0,    5.0),
        ("skill_coverage_pct",           0.0,  100.0),
        ("avg_skill_level",              0.0,    5.0),
        ("mandatory_skill_gap_count",    0.0,   10.0),
        ("cert_completion_rate",         0.0,    1.0),
        ("project_completion_rate",      0.0,    1.0),
        ("lead_project_completion_rate", 0.0,    1.0),
        ("avg_project_rating",           0.0,    5.0),
        ("current_grade_encoded",        1.0,    5.0),
        ("target_grade_encoded",         1.0,    5.0),
        ("grade_gap",                    0.0,    4.0),
        ("skill_score",                  0.0,   40.0),
        ("cert_score",                   0.0,   15.0),
        ("experience_score",             0.0,   15.0),
        ("project_score",                0.0,   20.0),
        ("performance_score",            0.0,   10.0),
        ("readiness_score",              0.0,  100.0),
    ]

    def validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate that all feature columns are present and clip to valid ranges.

        Args:
            df: Raw feature DataFrame (may include the target column).

        Returns:
            Cleaned DataFrame with features clipped to valid ranges.

        Raises:
            ValueError: If any expected feature column is missing.
        """
        missing_cols = [c for c in FEATURE_NAMES if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Feature DataFrame is missing columns: {missing_cols}"
            )

        df = df.copy()
        for col, lo, hi in self._CLIP_RULES:
            df[col] = df[col].clip(lower=lo, upper=hi)

        logger.info(
            "DataFrameFeatureEngineer: validated %d rows, %d feature columns.",
            len(df),
            len(FEATURE_NAMES),
        )
        return df

    def get_X_y(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Split a labelled DataFrame into feature matrix X and target vector y.

        Args:
            df: DataFrame containing both feature columns and TARGET_COLUMN.

        Returns:
            (X, y) where X has shape (n, 18) and y has shape (n,).

        Raises:
            ValueError: If TARGET_COLUMN is not present in df.
        """
        if TARGET_COLUMN not in df.columns:
            raise ValueError(
                f"Target column '{TARGET_COLUMN}' not found in DataFrame."
            )
        df_clean = self.validate_and_clean(df)
        X = df_clean[FEATURE_NAMES]
        y = df_clean[TARGET_COLUMN].astype(int)
        return X, y
