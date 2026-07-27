"""
Certification gap service.

Compares an employee's completed certifications against
the certification requirements of the target grade.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class CertificationGapService:
    """Identifies missing or incomplete certifications."""

    def analyze(self, employee: Employee, requirement: GradeRequirement) -> list[dict]:
        """
        Compare employee certifications against grade certification requirements.

        A certification is considered met only when its status is 'Completed'
        (matching the DB ENUM value exactly, case-insensitive).

        Args:
            employee:    The loaded Employee object.
            requirement: The loaded GradeRequirement object.

        Returns:
            List of dicts, one per missing certification:
            {
                "certification": str,
                "provider": str,
                "mandatory": bool
            }
        """
        completed: set[str] = {
            c.certification_name.lower()
            for c in employee.certifications
            if c.status.lower() == "completed"
        }

        gaps: list[dict] = []

        for req in requirement.certifications:
            if req.certification_name.lower() not in completed:
                gaps.append({
                    "certification": req.certification_name,
                    "provider": req.provider,
                    "mandatory": req.mandatory,
                })

        logger.info(
            "Certification gap analysis for employee %s: %d gap(s) found.",
            employee.employee_id,
            len(gaps),
        )
        return gaps
