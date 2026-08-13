"""
Gap analysis service.

Orchestrates the full gap analysis pipeline:
loads employee and grade data, delegates to each gap service,
and merges all results into a single Python dictionary.
"""

import logging
from typing import Optional

from services.data_loader import DataLoader
from services.skill_gap_service import SkillGapService
from services.certification_gap_service import CertificationGapService
from services.experience_gap_service import ExperienceGapService
from services.project_gap_service import ProjectGapService
from models.employee import Employee
from models.grade_requirement import GradeRequirement

logger = logging.getLogger(__name__)


class EmployeeNotFoundError(Exception):
    """Raised when the requested employee does not exist."""


class GradeNotFoundError(Exception):
    """Raised when the target grade requirement record does not exist."""


class GapAnalysisService:
    """
    Orchestrates the end-to-end gap analysis for a given employee.

    Uses DataLoader to fetch data and delegates gap calculations
    to the individual gap services.
    """

    def __init__(self) -> None:
        """Initialise the data loader and all gap services."""
        self._loader = DataLoader()
        self._skill_svc = SkillGapService()
        self._cert_svc = CertificationGapService()
        self._exp_svc = ExperienceGapService()
        self._proj_svc = ProjectGapService()

    def close(self) -> None:
        """Release database connections back to the pool."""
        self._loader.close()

    def run(self, employee_id: int, target_grade_id: Optional[int] = None) -> dict:
        """
        Execute the full gap analysis for the given employee against a target grade.

        Args:
            employee_id: The primary key of the employee to analyse.
            target_grade_id: Optional target grade ID. Defaults to employee's target_grade_id.

        Returns:
            A dict containing employee details and all gap results.

        Raises:
            EmployeeNotFoundError: If the employee does not exist.
            GradeNotFoundError:    If the target grade has no requirement record.
        """
        employee: Optional[Employee] = self._loader.load_employee(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found.")

        target_id = target_grade_id if target_grade_id is not None else employee.target_grade_id
        requirement: Optional[GradeRequirement] = self._loader.load_grade_requirement(target_id)
        if requirement is None:
            raise GradeNotFoundError(
                f"Grade requirement for grade_id={target_id} not found."
            )


        skill_gaps = self._skill_svc.analyze(employee, requirement)
        cert_gaps = self._cert_svc.analyze(employee, requirement)
        exp_gap = self._exp_svc.analyze(employee, requirement)
        proj_gap = self._proj_svc.analyze(employee, requirement)

        logger.info("Gap analysis complete for employee %s.", employee_id)

        return {
            "employee": employee,
            "requirement": requirement,
            "skill_gaps": skill_gaps,
            "certification_gaps": cert_gaps,
            "experience_gap": exp_gap,
            "project_gap": proj_gap,
        }
