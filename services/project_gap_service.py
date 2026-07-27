"""
Project gap service.

Compares an employee's completed and lead projects against
the project requirements of the target grade.
"""

import logging

from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class ProjectGapService:
    """Calculates the project and lead-project gaps."""

    def analyze(self, employee: Employee, requirement: GradeRequirement) -> dict:
        """
        Compare employee project counts against grade requirements.

        Never returns negative remaining values.

        Args:
            employee:    The loaded Employee object.
            requirement: The loaded GradeRequirement object.

        Returns:
            Dict with:
            {
                "total_projects": int,
                "lead_projects": int,
                "required_projects": int,
                "required_lead_projects": int,
                "remaining_projects": int,      # always >= 0
                "remaining_lead_projects": int  # always >= 0
            }
        """
        if requirement.project_requirement is None:
            min_projects = 0
            min_lead = 0
        else:
            min_projects = requirement.project_requirement.minimum_projects
            min_lead = requirement.project_requirement.minimum_lead_projects

        total_projects = len(employee.projects)
        lead_projects = sum(1 for p in employee.projects if p.lead_project)

        remaining_projects = max(min_projects - total_projects, 0)
        remaining_lead = max(min_lead - lead_projects, 0)

        logger.info(
            "Project gap for employee %s: total=%d lead=%d required=%d required_lead=%d",
            employee.employee_id,
            total_projects,
            lead_projects,
            min_projects,
            min_lead,
        )

        return {
            "total_projects": total_projects,
            "lead_projects": lead_projects,
            "required_projects": min_projects,
            "required_lead_projects": min_lead,
            "remaining_projects": remaining_projects,
            "remaining_lead_projects": remaining_lead,
        }
