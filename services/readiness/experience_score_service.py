"""
Experience Score Service — Phase 3.

Calculates the experience component of the promotion readiness score
from the gap analysis output produced by Phase 2.
"""

import logging
from dataclasses import dataclass

from models.employee import Employee

logger = logging.getLogger(__name__)

# Experience contributes 15 points to the overall 100-point readiness score.
EXPERIENCE_MAX_SCORE: float = 15.0


@dataclass
class ExperienceScoreResult:
    """Result of the experience scoring calculation."""

    current_years: float
    required_years: float
    gap_years: float
    score: float


class ExperienceScoreService:
    """
    Scores an employee's experience against the target grade requirement.

    Formula: min(current / required, 1.0) × EXPERIENCE_MAX_SCORE
    Score is capped at EXPERIENCE_MAX_SCORE — exceeding the requirement
    does not yield bonus points.
    """

    def calculate(
        self,
        employee: Employee,
        experience_gap: dict,
    ) -> ExperienceScoreResult:
        """
        Calculate the experience readiness score.

        Args:
            employee:        The loaded Employee object.
            experience_gap:  The experience_gap dict produced by Phase 2
                             ExperienceGapService (keys: current_years,
                             required_years, remaining_years).

        Returns:
            ExperienceScoreResult with current, required, gap, and score.
        """
        current: float = experience_gap["current_years"]
        required: float = experience_gap["required_years"]
        gap: float = experience_gap["remaining_years"]

        if required == 0.0:
            score = EXPERIENCE_MAX_SCORE
        else:
            ratio = min(current / required, 1.0)
            score = round(ratio * EXPERIENCE_MAX_SCORE, 2)

        logger.info(
            "Experience score for employee %s: %.2f / %.2f (current=%.1f required=%.1f)",
            employee.employee_id,
            score,
            EXPERIENCE_MAX_SCORE,
            current,
            required,
        )

        return ExperienceScoreResult(
            current_years=current,
            required_years=required,
            gap_years=gap,
            score=score,
        )
