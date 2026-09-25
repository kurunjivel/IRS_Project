"""
Profile Update Service for confirmed resume changes.
Updates employee profile only after explicit employee confirmation.
"""

import logging
from typing import Dict, List, Any, Optional

from database.employee_repository import EmployeeRepository

logger = logging.getLogger(__name__)


class ProfileUpdateService:
    """
    Applies employee-confirmed resume updates to the database.
    """

    def __init__(self, emp_repo: Optional[EmployeeRepository] = None) -> None:
        self.emp_repo = emp_repo or EmployeeRepository()

    def confirm_and_apply_updates(
        self,
        employee_id: int,
        confirmed_skills: List[Dict[str, Any]],
        confirmed_certifications: List[Dict[str, Any]],
        confirmed_projects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Apply confirmed updates to employee profile in database.

        Args:
            employee_id: Unique positive integer employee ID.
            confirmed_skills: List of confirmed skill dicts.
            confirmed_certifications: List of confirmed certification dicts.
            confirmed_projects: List of confirmed project dicts.

        Returns:
            Dict summary of applied changes and updated profile stats.
        """
        logger.info(
            "Applying confirmed profile updates for employee_id=%s (skills=%d, certs=%d, projects=%d)",
            employee_id, len(confirmed_skills), len(confirmed_certifications), len(confirmed_projects),
        )

        success = self.emp_repo.update_employee_profile_data(
            employee_id=employee_id,
            confirmed_skills=confirmed_skills,
            confirmed_certs=confirmed_certifications,
            confirmed_projects=confirmed_projects,
        )

        updated_skills = self.emp_repo.get_employee_skills(employee_id)
        updated_certs = self.emp_repo.get_employee_certifications(employee_id)
        updated_projects = self.emp_repo.get_employee_projects(employee_id)

        return {
            "status": "SUCCESS" if success else "FAILED",
            "employee_id": employee_id,
            "applied_updates": {
                "skills_added_or_upgraded": len(confirmed_skills),
                "certifications_added": len(confirmed_certifications),
                "projects_added": len(confirmed_projects),
            },
            "updated_profile_summary": {
                "total_skills": len(updated_skills),
                "total_certifications": len(updated_certs),
                "total_projects": len(updated_projects),
            },
        }
