"""
Experience gap service.

Compares an employee's years of experience against
the minimum experience required by the target grade.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class ExperienceGapService:
    """Calculates the experience gap between employee and target grade."""

    def analyze(self, employee: Employee, requirement: GradeRequirement) -> dict:
        """
        Compare employee experience against the grade minimum.

        Never returns a negative remaining value.

        Args:
            employee:    The loaded Employee object.
            requirement: The loaded GradeRequirement object.

        Returns:
            Dict with:
            {
                "current_years": float,
                "required_years": float,
                "remaining_years": float   # always >= 0
            }
        """
        required = (
            requirement.project_requirement.minimum_experience
            if requirement.project_requirement
            else 0.0
        )

        current = employee.experience_years
        remaining = max(required - current, 0.0)

        logger.info(
            "Experience gap for employee %s: current=%.1f required=%.1f remaining=%.1f",
            employee.employee_id,
            current,
            required,
            remaining,
        )

        return {
            "current_years": current,
            "required_years": required,
            "remaining_years": remaining,
        }
