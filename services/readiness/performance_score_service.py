"""
Performance Score Service — Phase 3.

Calculates the performance component of the promotion readiness score
from the employee's performance rating.
"""

import logging
from dataclasses import dataclass

from models.employee import Employee

logger = logging.getLogger(__name__)

# Performance contributes 10 points to the overall 100-point readiness score.
PERFORMANCE_MAX_SCORE: float = 10.0
PERFORMANCE_RATING_MAX: float = 5.0


@dataclass
class PerformanceScoreResult:
    """Result of the performance scoring calculation."""

    performance_rating: float
    score: float


class PerformanceScoreService:
    """
    Scores an employee's performance rating.

    Formula: (performance_rating / PERFORMANCE_RATING_MAX) × PERFORMANCE_MAX_SCORE
    Score is capped at PERFORMANCE_MAX_SCORE.
    """

    def calculate(self, employee: Employee) -> PerformanceScoreResult:
        """
        Calculate the performance readiness score.

        Args:
            employee: The loaded Employee object.

        Returns:
            PerformanceScoreResult with the raw rating and computed score.
        """
        rating = max(0.0, min(employee.performance_rating, PERFORMANCE_RATING_MAX))
        score = round((rating / PERFORMANCE_RATING_MAX) * PERFORMANCE_MAX_SCORE, 2)

        logger.info(
            "Performance score for employee %s: %.2f / %.2f (rating=%.1f)",
            employee.employee_id,
            score,
            PERFORMANCE_MAX_SCORE,
            rating,
        )

        return PerformanceScoreResult(
            performance_rating=rating,
            score=score,
        )
