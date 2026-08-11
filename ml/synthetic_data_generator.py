"""
Synthetic Dataset Generator — IRS Phase 4.

IMPORTANT — DATA DISCLAIMER
============================
All data produced by this module is SYNTHETIC and ACADEMIC.
It was generated programmatically for demonstration and model-training
purposes only.  It does NOT represent any real employee, organisation,
HR record, or promotion decision.

Design goals
------------
* Realistic feature distributions that mirror what a real HR dataset
  would contain (experience years, skill levels, certification rates, etc.)
* A deterministic promotion_success label derived from a transparent,
  rule-based formula so the ML model has a learnable signal.
* Controlled class balance (roughly 55 % promoted / 45 % not promoted)
  to avoid a trivially imbalanced dataset.
* No protected or sensitive personal attributes (race, gender, religion,
  health, etc.) — only job-relevant factors.
* Reproducible via a fixed random seed.

Feature columns produced
------------------------
experience_years            float   0.5 – 20.0
performance_rating          float   1.0 – 5.0
skill_coverage_pct          float   0.0 – 100.0   % of required skills held
avg_skill_level             float   0.0 – 5.0
mandatory_skill_gap_count   int     0 – 10
cert_completion_rate        float   0.0 – 1.0
project_completion_rate     float   0.0 – 1.0
lead_project_completion_rate float  0.0 – 1.0
avg_project_rating          float   0.0 – 5.0
current_grade_encoded       int     1 – 5   (ordinal: G1 lowest, G5 highest)
target_grade_encoded        int     1 – 5
grade_gap                   int     1 – 2   (target − current, always ≥ 1)
skill_score                 float   0.0 – 40.0
cert_score                  float   0.0 – 15.0
experience_score            float   0.0 – 15.0
project_score               float   0.0 – 20.0
performance_score           float   0.0 – 10.0
readiness_score             float   0.0 – 100.0

Target column
-------------
promotion_success           int     0 = did not progress, 1 = progressed
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYNTHETIC_DATA_DISCLAIMER: str = (
    "SYNTHETIC ACADEMIC DATA — Not real HR data. "
    "Generated for IRS demonstration and ML training purposes only."
)

# Scoring maxima — kept in sync with Phase 3 constants.
_SKILL_MAX: float = 40.0
_CERT_MAX: float = 15.0
_EXP_MAX: float = 15.0
_PROJ_MAX: float = 20.0
_PERF_MAX: float = 10.0

# Grade labels used for ordinal encoding.
_GRADE_LABELS: list[str] = ["G1", "G2", "G3", "G4", "G5"]
_GRADE_TO_INT: dict[str, int] = {g: i + 1 for i, g in enumerate(_GRADE_LABELS)}

# Promotion decision thresholds (mirrors Phase 3 ReadinessReportBuilder).
_READY_THRESHOLD: float = 90.0
_CONDITIONAL_THRESHOLD: float = 60.0

# Noise scale applied to the readiness score when deriving the label,
# so the boundary is not perfectly sharp (more realistic).
_LABEL_NOISE_SCALE: float = 8.0


@dataclass
class SyntheticDatasetConfig:
    """
    Configuration for the synthetic dataset generator.

    Attributes:
        n_samples:   Total number of employee-progression records to generate.
        random_seed: NumPy random seed for full reproducibility.
        grade_pairs: List of (current_grade, target_grade) tuples to sample from.
                     Each pair must satisfy target > current.
    """

    n_samples: int = 1_000
    random_seed: int = 42
    grade_pairs: list[tuple[str, str]] = field(default_factory=lambda: [
        ("G1", "G2"),
        ("G2", "G3"),
        ("G3", "G4"),
        ("G4", "G5"),
        ("G1", "G2"),   # repeated to weight lower grades more heavily
        ("G2", "G3"),
    ])


class SyntheticDatasetGenerator:
    """
    Generates a synthetic, clearly-labelled employee progression dataset.

    The dataset is designed to be realistic enough for ML training while
    being entirely fabricated — no real personal data is used or implied.

    Usage
    -----
    >>> gen = SyntheticDatasetGenerator()
    >>> df  = gen.generate()
    >>> print(df.shape)
    (1000, 19)
    """

    def __init__(self, config: SyntheticDatasetConfig | None = None) -> None:
        self._cfg = config or SyntheticDatasetConfig()
        self._rng = np.random.default_rng(self._cfg.random_seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> pd.DataFrame:
        """
        Generate the full synthetic dataset.

        Returns:
            A pandas DataFrame with one row per synthetic employee-progression
            record.  The final column is ``promotion_success`` (0 or 1).
            The DataFrame carries a ``disclaimer`` attribute.
        """
        n = self._cfg.n_samples
        logger.info("Generating %d synthetic employee-progression records.", n)

        raw = self._sample_raw_features(n)
        scores = self._compute_scores(raw)
        labels = self._derive_labels(scores["readiness_score"])

        df = pd.DataFrame({
            # --- raw job-relevant features ---
            "experience_years":             raw["experience_years"],
            "performance_rating":           raw["performance_rating"],
            "skill_coverage_pct":           raw["skill_coverage_pct"],
            "avg_skill_level":              raw["avg_skill_level"],
            "mandatory_skill_gap_count":    raw["mandatory_skill_gap_count"],
            "cert_completion_rate":         raw["cert_completion_rate"],
            "project_completion_rate":      raw["project_completion_rate"],
            "lead_project_completion_rate": raw["lead_project_completion_rate"],
            "avg_project_rating":           raw["avg_project_rating"],
            "current_grade_encoded":        raw["current_grade_encoded"],
            "target_grade_encoded":         raw["target_grade_encoded"],
            "grade_gap":                    raw["grade_gap"],
            # --- Phase 3 derived scores ---
            "skill_score":                  scores["skill_score"],
            "cert_score":                   scores["cert_score"],
            "experience_score":             scores["experience_score"],
            "project_score":                scores["project_score"],
            "performance_score":            scores["performance_score"],
            "readiness_score":              scores["readiness_score"],
            # --- target variable ---
            "promotion_success":            labels,
        })

        # Attach disclaimer as a DataFrame attribute (survives to_csv header comment).
        df.attrs["disclaimer"] = SYNTHETIC_DATA_DISCLAIMER

        promotion_rate = labels.mean()
        logger.info(
            "Dataset generated: %d rows, %d features + 1 target. "
            "Promotion rate: %.1f%%.",
            len(df),
            len(df.columns) - 1,
            promotion_rate * 100,
        )
        return df

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sample_raw_features(self, n: int) -> dict[str, np.ndarray]:
        """Sample raw feature arrays for n records."""
        rng = self._rng

        # --- Grade pair assignment ---
        pair_indices = rng.integers(0, len(self._cfg.grade_pairs), size=n)
        current_grades = np.array([self._cfg.grade_pairs[i][0] for i in pair_indices])
        target_grades  = np.array([self._cfg.grade_pairs[i][1] for i in pair_indices])
        current_encoded = np.array([_GRADE_TO_INT[g] for g in current_grades])
        target_encoded  = np.array([_GRADE_TO_INT[g] for g in target_grades])
        grade_gap = target_encoded - current_encoded  # always >= 1

        # --- Experience: higher grades require more experience ---
        # Base experience scales with current grade level.
        exp_base = current_encoded * 2.0          # G1→2, G2→4, G3→6, G4→8
        experience_years = np.clip(
            rng.normal(loc=exp_base, scale=2.5, size=n), 0.5, 20.0
        ).round(1)

        # --- Performance rating: 1.0 – 5.0 ---
        performance_rating = np.clip(
            rng.normal(loc=3.5, scale=0.8, size=n), 1.0, 5.0
        ).round(2)

        # --- Skill coverage: % of required skills the employee holds ---
        skill_coverage_pct = np.clip(
            rng.beta(a=5, b=2, size=n) * 100, 0.0, 100.0
        ).round(2)

        # --- Average skill level: 0 – 5 ---
        avg_skill_level = np.clip(
            rng.normal(loc=3.0, scale=1.0, size=n), 0.0, 5.0
        ).round(2)

        # --- Mandatory skill gap count: 0 – 10 ---
        # Inversely correlated with skill_coverage_pct.
        gap_prob = 1.0 - (skill_coverage_pct / 100.0)
        mandatory_skill_gap_count = np.clip(
            rng.binomial(n=10, p=gap_prob, size=n), 0, 10
        ).astype(int)

        # --- Certification completion rate: 0.0 – 1.0 ---
        cert_completion_rate = np.clip(
            rng.beta(a=4, b=2, size=n), 0.0, 1.0
        ).round(3)

        # --- Project completion rate: 0.0 – 1.0 ---
        project_completion_rate = np.clip(
            rng.beta(a=5, b=2, size=n), 0.0, 1.0
        ).round(3)

        # --- Lead project completion rate: 0.0 – 1.0 ---
        # Typically lower than overall project rate.
        lead_project_completion_rate = np.clip(
            project_completion_rate * rng.uniform(0.3, 1.0, size=n), 0.0, 1.0
        ).round(3)

        # --- Average project rating: 0.0 – 5.0 ---
        avg_project_rating = np.clip(
            rng.normal(loc=3.5, scale=0.7, size=n), 0.0, 5.0
        ).round(2)

        return {
            "experience_years":             experience_years,
            "performance_rating":           performance_rating,
            "skill_coverage_pct":           skill_coverage_pct,
            "avg_skill_level":              avg_skill_level,
            "mandatory_skill_gap_count":    mandatory_skill_gap_count,
            "cert_completion_rate":         cert_completion_rate,
            "project_completion_rate":      project_completion_rate,
            "lead_project_completion_rate": lead_project_completion_rate,
            "avg_project_rating":           avg_project_rating,
            "current_grade_encoded":        current_encoded,
            "target_grade_encoded":         target_encoded,
            "grade_gap":                    grade_gap,
        }

    def _compute_scores(self, raw: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """
        Derive Phase-3-equivalent scores from raw features.

        These mirror the exact formulas used in Phase 3 scoring services
        so the ML model can learn from both raw features and derived scores.
        """
        skill_score = np.round(
            (raw["skill_coverage_pct"] / 100.0) * _SKILL_MAX, 2
        )

        cert_score = np.round(
            raw["cert_completion_rate"] * _CERT_MAX, 2
        )

        # Experience score: ratio capped at 1.0, scaled to EXP_MAX.
        # Required experience approximated as (target_grade_encoded * 2).
        required_exp = raw["target_grade_encoded"] * 2.0
        exp_ratio = np.minimum(raw["experience_years"] / required_exp, 1.0)
        experience_score = np.round(exp_ratio * _EXP_MAX, 2)

        # Project score: 70 % total, 30 % lead (mirrors Phase 3 split).
        project_score = np.round(
            raw["project_completion_rate"] * _PROJ_MAX * 0.70
            + raw["lead_project_completion_rate"] * _PROJ_MAX * 0.30,
            2,
        )

        performance_score = np.round(
            (raw["performance_rating"] / 5.0) * _PERF_MAX, 2
        )

        readiness_score = np.round(
            skill_score + cert_score + experience_score
            + project_score + performance_score,
            2,
        )

        return {
            "skill_score":       skill_score,
            "cert_score":        cert_score,
            "experience_score":  experience_score,
            "project_score":     project_score,
            "performance_score": performance_score,
            "readiness_score":   readiness_score,
        }

    def _derive_labels(self, readiness_score: np.ndarray) -> np.ndarray:
        """
        Derive the binary promotion_success label.

        The label is primarily driven by readiness_score with added Gaussian
        noise so the decision boundary is not perfectly sharp — this makes
        the dataset more realistic and prevents the ML model from simply
        memorising the Phase 3 threshold.

        Label rule (after noise):
            score >= 65  →  promotion_success = 1  (promoted)
            score <  65  →  promotion_success = 0  (not promoted)

        The 65-point threshold (rather than Phase 3's 60-point "Conditional"
        boundary) is intentional: it creates a realistic scenario where some
        employees who are "Conditional" by the rule-based system did not
        actually get promoted, and some who scored slightly below 60 did —
        giving the ML model something genuinely useful to learn.
        """
        noisy_score = readiness_score + self._rng.normal(
            loc=0.0, scale=_LABEL_NOISE_SCALE, size=len(readiness_score)
        )
        labels = (noisy_score >= 65.0).astype(int)
        return labels
