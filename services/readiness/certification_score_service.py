"""
Certification Score Service — Phase 3.

Calculates the certification component of the promotion readiness score
from the gap analysis output produced by Phase 2.
"""

import logging
from dataclasses import dataclass

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)

# Certifications contribute 15 points to the overall 100-point readiness score.
CERTIFICATION_MAX_SCORE: float = 15.0


@dataclass
class CertificationScoreResult:
    """Result of the certification scoring calculation."""

    score: float
    max_score: float
    completed: int
    missing: list[str]


class CertificationScoreService:
    """
    Scores an employee's certifications against the target grade requirements.

    Each required certification is worth an equal share of CERTIFICATION_MAX_SCORE.
    Missing certifications receive 0 points.
    """

    def calculate(
        self,
        employee: Employee,
        requirement: GradeRequirement,
        certification_gaps: list[dict],
    ) -> CertificationScoreResult:
        """
        Calculate the certification readiness score.

        Args:
            employee:             The loaded Employee object.
            requirement:          The loaded GradeRequirement object.
            certification_gaps:   The certification_gaps list from Phase 2.

        Returns:
            CertificationScoreResult with score, max_score, completed count,
            and list of missing certification names.
        """
        total_required = len(requirement.certifications)

        if total_required == 0:
            logger.info(
                "No certification requirements defined — awarding full certification score."
            )
            return CertificationScoreResult(
                score=CERTIFICATION_MAX_SCORE,
                max_score=CERTIFICATION_MAX_SCORE,
                completed=0,
                missing=[],
            )

        missing_names: list[str] = [g["certification"] for g in certification_gaps]
        missing_count = len(missing_names)
        completed_count = total_required - missing_count

        points_per_cert = CERTIFICATION_MAX_SCORE / total_required
        score = round(completed_count * points_per_cert, 2)

        logger.info(
            "Certification score for employee %s: %.2f / %.2f (%d/%d completed)",
            employee.employee_id,
            score,
            CERTIFICATION_MAX_SCORE,
            completed_count,
            total_required,
        )

        return CertificationScoreResult(
            score=score,
            max_score=CERTIFICATION_MAX_SCORE,
            completed=completed_count,
            missing=missing_names,
        )
