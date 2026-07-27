"""
Data loader service.

Responsible for orchestrating repository calls and assembling
fully populated Employee and GradeRequirement model objects.
"""

import logging
from typing import Optional

from database.employee_repository import EmployeeRepository
from database.grade_repository import GradeRepository
from models.employee import (
    Employee,
    EmployeeCertification,
    EmployeeProject,
    EmployeeSkill,
)
from models.grade_requirement import (
    GradeCertificationRequirement,
    GradeProjectRequirement,
    GradeRequirement,
    GradeSkillRequirement,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and assembles Employee and GradeRequirement objects
    from the database using the repository layer.
    """

    def __init__(self) -> None:
        """Initialise repositories, each borrowing one pooled connection."""
        self._emp_repo = EmployeeRepository()
        self._grade_repo = GradeRepository()

    def close(self) -> None:
        """Return all borrowed connections back to the pool."""
        self._emp_repo.close()
        self._grade_repo.close()

    def load_employee(self, employee_id: int) -> Optional[Employee]:
        """
        Load a fully populated Employee object for the given ID.

        Args:
            employee_id: The primary key of the employee.

        Returns:
            A populated Employee object, or None if the employee does not exist.
        """
        raw = self._emp_repo.get_employee(employee_id)
        if raw is None:
            logger.warning("Employee %s not found.", employee_id)
            return None

        employee = Employee(
            employee_id=raw["employee_id"],
            employee_code=raw["employee_code"],
            full_name=raw["full_name"],
            email=raw["email"],
            department=raw["department"],
            experience_years=float(raw["experience_years"]),
            performance_rating=float(raw["performance_rating"]),
            joining_date=str(raw["joining_date"]),
            current_grade=raw["current_grade"],
            current_grade_id=raw["current_grade_id"],
            target_grade=raw["target_grade"],
            target_grade_id=raw["target_grade_id"],
        )

        employee.skills = [
            EmployeeSkill(
                skill_name=row["skill_name"],
                category=row["category"],
                skill_level=int(row["skill_level"]),
            )
            for row in self._emp_repo.get_employee_skills(employee_id)
        ]

        employee.certifications = [
            EmployeeCertification(
                certification_name=row["certification_name"],
                provider=row["provider"],
                status=row["status"],
                completion_date=str(row["completion_date"]) if row["completion_date"] else None,
                expiry_date=str(row["expiry_date"]) if row["expiry_date"] else None,
            )
            for row in self._emp_repo.get_employee_certifications(employee_id)
        ]

        employee.projects = [
            EmployeeProject(
                project_name=row["project_name"],
                technology=row["technology"],
                difficulty=row["difficulty"],
                domain=row["domain"],
                role=row["role"],
                lead_project=bool(row["lead_project"]),
                duration_months=int(row["duration_months"]),
                project_rating=float(row["project_rating"]) if row["project_rating"] else None,
            )
            for row in self._emp_repo.get_employee_projects(employee_id)
        ]

        logger.info("Employee %s loaded successfully.", employee_id)
        return employee

    def load_grade_requirement(self, grade_id: int) -> Optional[GradeRequirement]:
        """
        Load a fully populated GradeRequirement object for the given grade ID.

        Args:
            grade_id: The primary key of the target grade.

        Returns:
            A populated GradeRequirement object, or None if the grade does not exist.
        """
        raw_grade = self._grade_repo.get_grade(grade_id)
        if raw_grade is None:
            logger.warning("Grade %s not found.", grade_id)
            return None

        requirement = GradeRequirement(
            grade_id=raw_grade["grade_id"],
            grade_name=raw_grade["grade_name"],
            description=raw_grade.get("description"),
        )

        requirement.skills = [
            GradeSkillRequirement(
                skill_name=row["skill_name"],
                category=row["category"],
                required_level=int(row["required_level"]),
                weight=float(row["weight"]),
                mandatory=bool(row["mandatory"]),
            )
            for row in self._grade_repo.get_grade_skills(grade_id)
        ]

        requirement.certifications = [
            GradeCertificationRequirement(
                certification_name=row["certification_name"],
                provider=row["provider"],
                mandatory=bool(row["mandatory"]),
            )
            for row in self._grade_repo.get_grade_certifications(grade_id)
        ]

        raw_proj = self._grade_repo.get_grade_project_requirement(grade_id)
        if raw_proj:
            requirement.project_requirement = GradeProjectRequirement(
                minimum_projects=int(raw_proj["minimum_projects"]),
                minimum_lead_projects=int(raw_proj["minimum_lead_projects"]),
                minimum_experience=float(raw_proj["minimum_experience"]),
            )

        logger.info("Grade requirement %s loaded successfully.", grade_id)
        return requirement
