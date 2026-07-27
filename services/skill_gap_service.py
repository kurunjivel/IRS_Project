"""
Skill gap service.

Compares an employee's current skills and levels against
the skill requirements of the target grade.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class SkillGapService:
    """Identifies missing skills and insufficient skill levels."""

    def analyze(self, employee: Employee, requirement: GradeRequirement) -> list[dict]:
        """
        Compare employee skills against grade skill requirements.

        For each required skill:
        - If the employee does not have it at all, current_level is 0.
        - If the employee has it but below the required level, the gap is calculated.
        - If the employee meets or exceeds the required level, it is excluded.

        Args:
            employee:    The loaded Employee object.
            requirement: The loaded GradeRequirement object.

        Returns:
            List of dicts, one per skill gap:
            {
                "skill": str,
                "category": str,
                "current_level": int,
                "required_level": int,
                "gap": int,
                "mandatory": bool
            }
        """
        employee_skill_map: dict[str, int] = {
            s.skill_name.lower(): s.skill_level
            for s in employee.skills
        }

        gaps: list[dict] = []

        for req in requirement.skills:
            current_level = employee_skill_map.get(req.skill_name.lower(), 0)
            gap = req.required_level - current_level

            if gap > 0:
                gaps.append({
                    "skill": req.skill_name,
                    "category": req.category,
                    "current_level": current_level,
                    "required_level": req.required_level,
                    "gap": gap,
                    "mandatory": req.mandatory,
                })

        logger.info(
            "Skill gap analysis for employee %s: %d gap(s) found.",
            employee.employee_id,
            len(gaps),
        )
        return gaps
