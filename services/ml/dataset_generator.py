"""
Dataset Generator — IRS Phase 4.

Generates a synthetic historical employee progression dataset,
saves it to datasets/historical_employee_progression.csv, and
provides load/validate helpers for downstream use.

DISCLAIMER
----------
This dataset is synthetic and created for academic development/testing.
It does NOT represent any real employee, organisation, HR record, or
promotion decision.  All records were generated programmatically using
controlled random distributions.

Label generation — anti-leakage design
---------------------------------------
The promotion_success label is NOT derived by simply thresholding
readiness_score.  Instead it is computed from a weighted logistic
combination of independent raw features with added noise:

    logit = (
          0.30 × norm(experience_years)
        + 0.25 × norm(performance_rating)
        + 0.20 × norm(skill_coverage_percentage)
        + 0.15 × norm(project_completion_rate)
        + 0.10 × norm(lead_project_completion_rate)
        − 0.20 × norm(mandatory_skill_gap_count)
        − 0.15 × norm(mandatory_certification_gap_count)
        + noise(0, 0.5)
    )

    probability = sigmoid(logit)
    promotion_success = Bernoulli(probability)

This means:
- The label is influenced by multiple independent factors.
- It is NOT a deterministic function of readiness_score.
- The ML model must learn a pattern, not reproduce the Phase 3 formula.
- Noise ensures the boundary is not perfectly sharp.

Random state: 42 (deterministic, reproducible).
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from services.ml.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DISCLAIMER: str = (
    "This dataset is synthetic and created for academic development/testing. "
    "It does NOT represent any real employee, organisation, HR record, "
    "or promotion decision."
)

DEFAULT_OUTPUT_PATH: Path = (
    Path(__file__).resolve().parent.parent.parent / "datasets" / "historical_employee_progression.csv"
)

RANDOM_STATE: int = 42

# Grade ordinal encoding
_GRADE_PAIRS: list[tuple[str, str, int, int]] = [
    ("G1", "G2", 1, 2),
    ("G2", "G3", 2, 3),
    ("G3", "G4", 3, 4),
    ("G4", "G5", 4, 5),
    ("G1", "G2", 1, 2),  # weighted toward lower grades
    ("G2", "G3", 2, 3),
]

# Phase 3 scoring maxima
_SKILL_MAX: float = 40.0
_CERT_MAX: float = 15.0
_EXP_MAX: float = 15.0
_PROJ_MAX: float = 20.0
_PERF_MAX: float = 10.0


class DatasetGenerator:
    """
    Generates, saves, loads, and validates the synthetic progression dataset.

    Parameters
    ----------
    n_samples   : Number of records to generate (default 1 000, minimum 500).
    random_state: NumPy seed for full reproducibility (default 42).
    output_path : Where to write the CSV (default datasets/historical_employee_progression.csv).
    """

    def __init__(
        self,
        n_samples: int = 1_200,
        random_state: int = RANDOM_STATE,
        output_path: Path | str | None = None,
    ) -> None:
        if n_samples < 500:
            raise ValueError(f"n_samples must be >= 500, got {n_samples}.")
        self._n = n_samples
        self._rng = np.random.default_rng(random_state)
        self._path = Path(output_path) if output_path else DEFAULT_OUTPUT_PATH

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> pd.DataFrame:
        """
        Generate the synthetic dataset in memory.

        Returns:
            DataFrame with FEATURE_COLUMNS + TARGET_COLUMN.
            Carries a ``disclaimer`` attribute.
        """
        logger.info("Generating %d synthetic progression records (seed=%d).", self._n, RANDOM_STATE)

        raw = self._sample_raw(self._n)
        scores = self._compute_scores(raw)
        labels = self._derive_labels(raw)

        df = pd.DataFrame({
            # Employee
            "experience_years":   raw["experience_years"],
            "performance_rating": raw["performance_rating"],
            "current_grade_encoded": raw["current_encoded"],
            "target_grade_encoded":  raw["target_encoded"],
            "grade_gap":             raw["grade_gap"],
            # Skills
            "total_skills":               raw["total_skills"],
            "average_skill_level":        raw["average_skill_level"],
            "skill_coverage_percentage":  raw["skill_coverage_pct"],
            "mandatory_skill_gap_count":  raw["mandatory_skill_gap_count"],
            "weighted_skill_gap":         raw["weighted_skill_gap"],
            # Certifications
            "total_certifications":            raw["total_certifications"],
            "completed_certifications":        raw["completed_certifications"],
            "certification_completion_rate":   raw["cert_completion_rate"],
            "mandatory_certification_gap_count": raw["mandatory_cert_gap_count"],
            # Projects
            "total_projects":              raw["total_projects"],
            "completed_projects":          raw["total_projects"],   # all listed are completed
            "lead_projects":               raw["lead_projects"],
            "project_completion_rate":     raw["project_completion_rate"],
            "lead_project_completion_rate": raw["lead_completion_rate"],
            "average_project_rating":      raw["avg_project_rating"],
            # Phase 3 scores
            "skill_score":         scores["skill_score"],
            "certification_score": scores["cert_score"],
            "experience_score":    scores["experience_score"],
            "project_score":       scores["project_score"],
            "performance_score":   scores["performance_score"],
            "readiness_score":     scores["readiness_score"],
            # Target
            TARGET_COLUMN: labels,
        })

        df.attrs["disclaimer"] = DISCLAIMER
        promoted = int(labels.sum())
        logger.info(
            "Dataset generated: %d rows, %d features, promotion_rate=%.1f%%.",
            len(df), len(FEATURE_COLUMNS), promoted / len(df) * 100,
        )
        return df

    def save(self, df: pd.DataFrame | None = None) -> Path:
        """
        Save the dataset to CSV.

        Args:
            df: DataFrame to save.  If None, generate() is called first.

        Returns:
            Path to the saved CSV file.
        """
        if df is None:
            df = self.generate()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", newline="", encoding="utf-8") as fh:
            fh.write(f"# {DISCLAIMER}\n")
            df.to_csv(fh, index=False)
        logger.info("Dataset saved to %s (%d rows).", self._path, len(df))
        return self._path

    def load(self) -> pd.DataFrame:
        """
        Load the saved CSV dataset.

        Returns:
            Full DataFrame including TARGET_COLUMN.

        Raises:
            FileNotFoundError: If the CSV has not been generated yet.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self._path}. Call save() first."
            )
        df = pd.read_csv(self._path, comment="#")
        logger.info("Dataset loaded from %s: %d rows.", self._path, len(df))
        return df

    def validate(self, df: pd.DataFrame) -> list[str]:
        """
        Validate a dataset DataFrame and return a list of issues found.

        Checks:
        - All required columns present.
        - No unexpected null values.
        - Target column contains only 0 and 1.
        - No duplicate rows.
        - Numeric ranges for key columns.

        Args:
            df: DataFrame to validate.

        Returns:
            List of issue strings.  Empty list means the dataset is valid.
        """
        issues: list[str] = []

        # Column presence
        all_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
        missing = [c for c in all_cols if c not in df.columns]
        if missing:
            issues.append(f"Missing columns: {missing}")
            return issues  # can't check further without columns

        # Null values
        null_counts = df[all_cols].isnull().sum()
        for col, cnt in null_counts.items():
            if cnt > 0:
                issues.append(f"Column '{col}' has {cnt} null value(s).")

        # Target values
        bad_target = set(df[TARGET_COLUMN].unique()) - {0, 1}
        if bad_target:
            issues.append(f"TARGET_COLUMN contains unexpected values: {bad_target}")

        # Duplicates
        n_dups = df.duplicated().sum()
        if n_dups > 0:
            issues.append(f"{n_dups} duplicate row(s) found.")

        # Range checks
        _ranges = [
            ("experience_years",              0.0,  50.0),
            ("performance_rating",            1.0,   5.0),
            ("skill_coverage_percentage",     0.0, 100.0),
            ("certification_completion_rate", 0.0,   1.0),
            ("project_completion_rate",       0.0,   1.0),
            ("lead_project_completion_rate",  0.0,   1.0),
            ("readiness_score",               0.0, 100.0),
        ]
        for col, lo, hi in _ranges:
            out = df[(df[col] < lo) | (df[col] > hi)]
            if len(out) > 0:
                issues.append(
                    f"Column '{col}' has {len(out)} value(s) outside [{lo}, {hi}]."
                )

        if not issues:
            logger.info("Dataset validation passed: %d rows, no issues.", len(df))
        else:
            logger.warning("Dataset validation found %d issue(s).", len(issues))

        return issues

    @property
    def output_path(self) -> Path:
        """Absolute path to the dataset CSV file."""
        return self._path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sample_raw(self, n: int) -> dict[str, np.ndarray]:
        """Sample all raw feature arrays."""
        rng = self._rng

        # Grade pairs
        pair_idx = rng.integers(0, len(_GRADE_PAIRS), size=n)
        current_encoded = np.array([_GRADE_PAIRS[i][2] for i in pair_idx])
        target_encoded  = np.array([_GRADE_PAIRS[i][3] for i in pair_idx])
        grade_gap = target_encoded - current_encoded

        # Experience — scales with current grade
        exp_base = current_encoded * 2.0
        experience_years = np.clip(
            rng.normal(loc=exp_base, scale=2.5, size=n), 0.5, 20.0
        ).round(1)

        # Performance
        performance_rating = np.clip(
            rng.normal(loc=3.5, scale=0.8, size=n), 1.0, 5.0
        ).round(2)

        # Skills
        total_skills = np.clip(rng.integers(2, 12, size=n), 2, 15).astype(int)
        average_skill_level = np.clip(
            rng.normal(loc=3.0, scale=1.0, size=n), 0.0, 5.0
        ).round(2)
        skill_coverage_pct = np.clip(
            rng.beta(a=5, b=2, size=n) * 100, 0.0, 100.0
        ).round(2)
        gap_prob = 1.0 - (skill_coverage_pct / 100.0)
        mandatory_skill_gap_count = np.clip(
            rng.binomial(n=8, p=gap_prob, size=n), 0, 8
        ).astype(int)
        # weighted_skill_gap: gap_count × avg_weight (weight ~ Uniform(0.5, 1.0))
        avg_weight = rng.uniform(0.5, 1.0, size=n)
        weighted_skill_gap = np.round(mandatory_skill_gap_count * avg_weight, 4)

        # Certifications
        total_certifications = np.clip(rng.integers(0, 6, size=n), 0, 6).astype(int)
        cert_completion_rate = np.clip(
            rng.beta(a=4, b=2, size=n), 0.0, 1.0
        ).round(3)
        completed_certifications = np.round(
            total_certifications * cert_completion_rate
        ).astype(int)
        mandatory_cert_gap_count = np.clip(
            rng.binomial(n=3, p=1.0 - cert_completion_rate, size=n), 0, 3
        ).astype(int)

        # Projects
        total_projects = np.clip(rng.integers(0, 10, size=n), 0, 10).astype(int)
        required_projects = np.clip(
            current_encoded + rng.integers(1, 3, size=n), 2, 8
        ).astype(int)
        project_completion_rate = np.clip(
            np.where(required_projects > 0, total_projects / required_projects, 1.0),
            0.0, 1.0,
        ).round(3)
        lead_projects = np.clip(
            np.floor(total_projects * rng.uniform(0.0, 0.5, size=n)).astype(int),
            0, total_projects,
        ).astype(int)
        required_lead = np.clip(rng.integers(1, 3, size=n), 1, 3).astype(int)
        lead_completion_rate = np.clip(
            np.where(required_lead > 0, lead_projects / required_lead, 1.0),
            0.0, 1.0,
        ).round(3)
        avg_project_rating = np.clip(
            rng.normal(loc=3.5, scale=0.7, size=n), 0.0, 5.0
        ).round(2)

        return {
            "current_encoded":            current_encoded,
            "target_encoded":             target_encoded,
            "grade_gap":                  grade_gap,
            "experience_years":           experience_years,
            "performance_rating":         performance_rating,
            "total_skills":               total_skills,
            "average_skill_level":        average_skill_level,
            "skill_coverage_pct":         skill_coverage_pct,
            "mandatory_skill_gap_count":  mandatory_skill_gap_count,
            "weighted_skill_gap":         weighted_skill_gap,
            "total_certifications":       total_certifications,
            "completed_certifications":   completed_certifications,
            "cert_completion_rate":       cert_completion_rate,
            "mandatory_cert_gap_count":   mandatory_cert_gap_count,
            "total_projects":             total_projects,
            "lead_projects":              lead_projects,
            "project_completion_rate":    project_completion_rate,
            "lead_completion_rate":       lead_completion_rate,
            "avg_project_rating":         avg_project_rating,
        }

    def _compute_scores(self, raw: dict) -> dict[str, np.ndarray]:
        """Compute Phase-3-equivalent scores from raw features."""
        skill_score = np.round((raw["skill_coverage_pct"] / 100.0) * _SKILL_MAX, 2)
        cert_score  = np.round(raw["cert_completion_rate"] * _CERT_MAX, 2)

        required_exp = raw["target_encoded"] * 2.0
        exp_ratio = np.minimum(raw["experience_years"] / required_exp, 1.0)
        experience_score = np.round(exp_ratio * _EXP_MAX, 2)

        project_score = np.round(
            raw["project_completion_rate"] * _PROJ_MAX * 0.70
            + raw["lead_completion_rate"] * _PROJ_MAX * 0.30,
            2,
        )
        performance_score = np.round(
            (raw["performance_rating"] / 5.0) * _PERF_MAX, 2
        )
        readiness_score = np.round(
            skill_score + cert_score + experience_score + project_score + performance_score, 2
        )
        return {
            "skill_score":       skill_score,
            "cert_score":        cert_score,
            "experience_score":  experience_score,
            "project_score":     project_score,
            "performance_score": performance_score,
            "readiness_score":   readiness_score,
        }

    def _derive_labels(self, raw: dict) -> np.ndarray:
        """
        Derive promotion_success labels using a logistic model on raw features.

        This is intentionally NOT a simple threshold on readiness_score to
        prevent target leakage.  The ML model must learn a pattern.

        Formula:
            logit = weighted combination of normalised raw features + noise
            probability = sigmoid(logit)
            label = Bernoulli(probability)
        """
        rng = self._rng

        def _norm(arr: np.ndarray) -> np.ndarray:
            """Min-max normalise to [0, 1]."""
            lo, hi = arr.min(), arr.max()
            if hi == lo:
                return np.zeros_like(arr, dtype=float)
            return (arr - lo) / (hi - lo)

        logit = (
              0.30 * _norm(raw["experience_years"])
            + 0.25 * _norm(raw["performance_rating"])
            + 0.20 * _norm(raw["skill_coverage_pct"])
            + 0.15 * _norm(raw["project_completion_rate"])
            + 0.10 * _norm(raw["lead_completion_rate"])
            - 0.20 * _norm(raw["mandatory_skill_gap_count"])
            - 0.15 * _norm(raw["mandatory_cert_gap_count"])
            - 0.40  # bias: centres distribution → ~55% positive rate
            + rng.normal(loc=0.0, scale=0.60, size=self._n)
        )

        probability = 1.0 / (1.0 + np.exp(-logit * 3.0))  # scale logit for sharper signal
        labels = rng.binomial(n=1, p=probability, size=self._n)
        return labels
